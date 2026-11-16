import easyocr
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image


class Ocr:
    _processor = None
    _model = None

    @staticmethod
    def read_text(path):
        if Ocr._model is None:
            name = "microsoft/trocr-base-handwritten"
            Ocr._processor = TrOCRProcessor.from_pretrained(name)
            Ocr._model = VisionEncoderDecoderModel.from_pretrained(name)

        image = Image.open(path).convert("RGB")
        pixels = Ocr._processor(images=image, return_tensors="pt").pixel_values
        ids = Ocr._model.generate(pixels)
        return Ocr._processor.batch_decode(ids, skip_special_tokens=True)[0]


class Easyocr:
    _readers = {}

    @staticmethod
    def read_text(path, languages=("uk", "en")):
        key = tuple(languages)
        if key not in Easyocr._readers:
            Easyocr._readers[key] = easyocr.Reader(list(languages), gpu=True)
        results = Easyocr._readers[key].readtext(path, detail=0)
        return " ".join(results)