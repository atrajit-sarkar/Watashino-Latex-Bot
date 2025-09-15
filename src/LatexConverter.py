from subprocess import check_output, CalledProcessError, STDOUT, TimeoutExpired

from src.PreambleManager import PreambleManager
from src.LoggingServer import LoggingServer
import io
import re
import shutil
import os
import glob


class LatexConverter():

    logger = LoggingServer.getInstance()
    
    def __init__(self, preambleManager, userOptionsManager):
         self._preambleManager = preambleManager
         self._userOptionsManager = userOptionsManager

    def extractBoundingBox(self, dpi, pathToPdf):
        try:
            gs = self._get_gs_executable()
            bbox = check_output([gs, "-q", "-dBATCH", "-dNOPAUSE", "-sDEVICE=bbox", pathToPdf],
                                stderr=STDOUT).decode("ascii")
        except CalledProcessError:
            raise ValueError("Could not extract bounding box! Empty expression?")
        except FileNotFoundError:
            raise ValueError("Ghostscript not found. Please install Ghostscript and ensure 'gs', 'gswin64c' or 'gswin32c' is on PATH.")
        try:
            bounds = [int(_) for _ in bbox[bbox.index(":")+2:bbox.index("\n")].split(" ")]
        except ValueError:
            raise ValueError("Could not parse bounding box! Empty expression?")

        if bounds[0] == bounds[2] or bounds[1] == bounds[3]:
            self.logger.warn("Expression had zero width/height bbox!")
            raise ValueError("Empty expression!")

        hpad = 0.25 * 72  # 72 postscript points = 1 inch
        vpad = .1 * 72
        llc = bounds[:2]
        llc[0] -= hpad
        llc[1] -= vpad
        ruc = bounds[2:]
        ruc[0] += hpad
        ruc[1] += vpad
        size_factor = dpi/72
        width = (ruc[0]-llc[0])*size_factor
        height = (ruc[1]-llc[1])*size_factor
        translation_x = llc[0]
        translation_y = llc[1]
        return width, height, -translation_x, -translation_y
    
    def correctBoundingBoxAspectRaito(self, dpi, boundingBox, maxWidthToHeight=3, maxHeightToWidth=1):
        width, height, translation_x, translation_y = boundingBox
        size_factor = dpi/72
        if width>maxWidthToHeight*height:
            translation_y += (width/maxWidthToHeight-height)/2/size_factor
            height = width/maxWidthToHeight
        elif height>maxHeightToWidth*width:
            translation_x += (height/maxHeightToWidth-width)/2/size_factor
            width = height/maxHeightToWidth
        return width, height, translation_x, translation_y
        
    def getError(self, log):
        for idx, line in enumerate(log):
            if line[:2]=="! ":
                return "".join(log[idx:idx+2])
        
    def pdflatex(self, fileName):
        try:
            check_output([
                'pdflatex',
                '-interaction=nonstopmode',
                '-output-directory', 'build',
                fileName
            ], stderr=STDOUT, timeout=5)
        except CalledProcessError:
            with open(fileName[:-3] + "log", "r") as f:
                msg = self.getError(f.readlines())
                self.logger.debug(msg)
            raise ValueError(msg)
        except TimeoutExpired:
            msg = "Pdflatex has likely hung up and had to be killed. Congratulations!"
            raise ValueError(msg)
    
    def cropPdf(self, sessionId): # TODO: this is intersecting with the png part
        try:
            gs = self._get_gs_executable()
            bbox = check_output([gs, "-q", "-dBATCH", "-dNOPAUSE", "-sDEVICE=bbox", f"build/expression_file_{sessionId}.pdf"], 
                                stderr=STDOUT).decode("ascii")
        except FileNotFoundError:
            raise ValueError("Ghostscript not found. Please install Ghostscript and ensure it is on PATH.")
        llx, lly, urx, ury = tuple([int(_) for _ in bbox[bbox.index(":")+2:bbox.index("\n")].split(" ")])
        # Add configurable margin (points). Default 24pt (~1/3 inch) for comfortable whitespace.
        try:
            margin = float(os.environ.get("LATEXBOT_PDF_MARGIN_PT", "24"))
        except ValueError:
            margin = 24.0
        margin = max(0.0, margin)
        # Expand bbox by margin on all sides
        width_pts = (urx - llx) + int(2 * margin)
        height_pts = (ury - lly) + int(2 * margin)
        # Translate content so that original lower-left is at (margin, margin)
        offset_x = -llx + int(margin)
        offset_y = -lly + int(margin)
        out_pdf = f"build/expression_file_cropped_{sessionId}.pdf"
        in_pdf = f"build/expression_file_{sessionId}.pdf"
        # Set exact page size and translate content so the expression sits at origin
        try:
            check_output([gs, "-o", out_pdf, "-sDEVICE=pdfwrite",
                          f"-dDEVICEWIDTHPOINTS={width_pts}", f"-dDEVICEHEIGHTPOINTS={height_pts}", "-dFIXEDMEDIA",
                          "-c", f"<</PageOffset [{offset_x} {offset_y}]>> setpagedevice",
                          "-f", in_pdf], stderr=STDOUT)
        except FileNotFoundError:
            raise ValueError("Ghostscript not found. Please install Ghostscript and ensure it is on PATH.")
            
    def convertPdfToPng(self, dpi, sessionId, bbox):
        gs = self._get_gs_executable()
        out_png = f"build/expression_{sessionId}.png"
        in_pdf = f"build/expression_file_{sessionId}.pdf"
        width, height, tx, ty = bbox
        # Default to white background to avoid black/transparent appearance in some viewers.
        transparent = os.environ.get("LATEXBOT_TRANSPARENT", "").lower() in ("1", "true", "yes", "on")
        device = "pngalpha" if transparent else "png16m"
        args = [gs, "-o", out_png, f"-r{dpi}", f"-g{int(width)}x{int(height)}", "-dLastPage=1",
                "-sDEVICE=" + device,
                "-dTextAlphaBits=4", "-dGraphicsAlphaBits=4",
                "-c", f"<</Install {{{int(tx)} {int(ty)} translate}}>> setpagedevice",
                "-f", in_pdf]
        if not transparent:
            # White background for non-alpha device
            args.insert(6, "-dBackgroundColor=16#FFFFFF")
        try:
            check_output(args, stderr=STDOUT)
        except FileNotFoundError:
            raise ValueError("Ghostscript not found. Please install Ghostscript and ensure it is on PATH.")

    def convertExpression(self, expression, userId, sessionId, returnPdf = False):




        if r"\documentclass" in expression:
            fileString = expression
        else:
            try:
                preamble = self._preambleManager.getPreambleFromDatabase(userId)
                self.logger.debug("Preamble for userId %d found", userId)
            except KeyError:
                self.logger.debug("Preamble for userId %d not found, using default preamble", userId)
                preamble = self._preambleManager.getDefaultPreamble()
            finally:
                fileString = preamble+"\n\\begin{document}\n"+expression+"\n\\end{document}"

        os.makedirs("build", exist_ok=True)
        with open("build/expression_file_%s.tex"%sessionId, "w+") as f:
            f.write(fileString)
        
        dpi = self._userOptionsManager.getDpiOption(userId)
        
        try:
            try:
                self.pdflatex("build/expression_file_%s.tex"%sessionId)
            except FileNotFoundError:
                raise ValueError("pdflatex not found. Please install a LaTeX distribution (TeX Live or MiKTeX) and ensure 'pdflatex' is on PATH.")
                
            bbox = self.extractBoundingBox(dpi, "build/expression_file_%s.pdf"%sessionId)
            bbox = self.correctBoundingBoxAspectRaito(dpi, bbox)
            self.convertPdfToPng(dpi, sessionId, bbox)
            
            self.logger.debug("Generated image for %s", expression)
            
            with open("build/expression_%s.png"%sessionId, "rb") as f:
                imageBinaryStream = io.BytesIO(f.read())

            if returnPdf:
                is_full_document = (r"\documentclass" in expression)
                if is_full_document:
                    # Preserve full document layout and margins
                    with open("build/expression_file_%s.pdf"%sessionId, "rb") as f:
                        pdfBinaryStream = io.BytesIO(f.read())
                else:
                    self.cropPdf(sessionId)
                    with open("build/expression_file_cropped_%s.pdf"%sessionId, "rb") as f:
                        pdfBinaryStream = io.BytesIO(f.read())
                return imageBinaryStream, pdfBinaryStream
            else:
                return imageBinaryStream
                
        finally:
            # Cross-platform cleanup
            try:
                for f in glob.glob(os.path.join("build", f"*_{sessionId}.*")):
                    try:
                        os.remove(f)
                    except FileNotFoundError:
                        pass
            except Exception:
                pass

    def _get_gs_executable(self):
        # Try common Ghostscript executables across platforms
        for name in ("gs", "gswin64c", "gswin32c"):
            path = shutil.which(name)
            if path:
                return path
        # Fallback to 'gs' which will raise later if missing
        return "gs"
        
