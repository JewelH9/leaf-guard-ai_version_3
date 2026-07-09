"""
Converts the trained .keras models to TFLite format with float16 weight
compression, then validates that the converted models produce near-identical
outputs to the originals before you trust them for deployment.

Run this ONCE locally (venv has full TensorFlow already installed).
The output .tflite files are what actually get deployed — much lighter
than the .keras files at runtime.
"""
import tensorflow as tf
import numpy as np
import os

MODELS_DIR = os.path.join("backend", "models")

def convert_model(keras_path, tflite_path):
    print(f"\nLoading {keras_path}...")
    model = tf.keras.models.load_model(keras_path)

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_types = [tf.float16]  # ~50% smaller, negligible accuracy loss

    print(f"Converting to TFLite (float16)...")
    tflite_model = converter.convert()

    with open(tflite_path, "wb") as f:
        f.write(tflite_model)

    size_mb = os.path.getsize(tflite_path) / (1024 * 1024)
    print(f"Saved {tflite_path} ({size_mb:.1f} MB)")
    return model


def validate_conversion(keras_model, tflite_path, input_shape, n_samples=10):
    """Feed identical random inputs to both models and confirm outputs match closely.
    This proves the conversion preserved the model's math correctly."""
    interpreter = tf.lite.Interpreter(model_path=tflite_path)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    max_diffs = []
    for _ in range(n_samples):
        sample = np.random.uniform(0, 255, size=input_shape).astype(np.float32)

        keras_out = keras_model.predict(sample, verbose=0)

        interpreter.set_tensor(input_details[0]['index'], sample)
        interpreter.invoke()
        tflite_out = interpreter.get_tensor(output_details[0]['index'])

        max_diff = np.max(np.abs(keras_out - tflite_out))
        max_diffs.append(max_diff)

    avg_max_diff = np.mean(max_diffs)
    print(f"Validation over {n_samples} random samples — average max output difference: {avg_max_diff:.6f}")
    if avg_max_diff < 0.01:
        print("✅ Conversion looks safe — outputs match closely. Fine to deploy.")
    else:
        print("⚠️  Larger-than-expected difference. Review before deploying — consider skipping float16.")
    return avg_max_diff


if __name__ == "__main__":
    print("=" * 60)
    print("STAGE 1 (Leaf Detector)")
    print("=" * 60)
    stage1_model = convert_model(
        os.path.join(MODELS_DIR, "stage1_final.keras"),
        os.path.join(MODELS_DIR, "stage1_final.tflite")
    )
    validate_conversion(stage1_model, os.path.join(MODELS_DIR, "stage1_final.tflite"), input_shape=(1, 224, 224, 3))

    print("\n" + "=" * 60)
    print("STAGE 2 (Disease Classifier)")
    print("=" * 60)
    stage2_model = convert_model(
        os.path.join(MODELS_DIR, "stage2_final.keras"),
        os.path.join(MODELS_DIR, "stage2_final.tflite")
    )
    validate_conversion(stage2_model, os.path.join(MODELS_DIR, "stage2_final.tflite"), input_shape=(1, 224, 224, 3))

    print("\nDone. Deploy the .tflite files — you can leave the .keras files out of the Docker image now.")