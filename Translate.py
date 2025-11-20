from model import Model
import mlflow
import hashlib
import os


class Translater:
    def __init__(self):
        self.text = None
        self.target_language = None

    def translate(self, text, target_language):
        self.text = text
        self.target_language = target_language

        prompt = f"Translate the following text to {self.target_language}: {self.text}"

        # Usar MLflow local o contenedor
        mlflow.set_tracking_uri(os.getenv("MLFLOW_URI", "http://mlflow-server:5000"))
        mlflow.set_experiment("traduccion_genai")

        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]

        with mlflow.start_run(run_name=f"traduccion_{prompt_hash}"):

            mlflow.gemini.autolog()

            translated_text, len_answer, time_inferenced = Model.use(prompt)
            latency_ms = time_inferenced * 1000.0

            # Logs básicos
            mlflow.log_param("idioma_objetivo", target_language)
            mlflow.log_param("modelo", "gemini-2.5-flash")
            mlflow.log_metric("latency_ms", latency_ms)
            mlflow.log_metric("len_response", len_answer)

            # Artefactos (solo lo necesario)
            mlflow.log_text(text, "original_text.txt")
            mlflow.log_text(translated_text, "translated_text.txt")

        return translated_text, f"{latency_ms:.2f} ms"
