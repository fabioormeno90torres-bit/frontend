from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import os
from werkzeug.utils import secure_filename
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)
CORS(app)

# Carga del modelo TFLite
interpreter = tf.lite.Interpreter(model_path='brain_tumor_cnn.tflite')
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

class_names = ['glioma', 'meningioma', 'notumor', 'pituitary']

# Configuración de carpetas
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def predict_with_tflite(img_array):
    """Realiza la predicción usando el intérprete de TFLite"""
    img_array = img_array.astype(np.float32) / 255.0
    interpreter.set_tensor(input_details[0]['index'], img_array)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    return output_data[0]

@app.route('/api/clasificar', methods=['POST'])
def clasificar_api():
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'No se envió imagen'}), 400
    
    # Guardar archivo de forma segura
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Procesamiento de imagen
    img = image.load_img(filepath, target_size=(128, 128))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    
    # Predicción
    prediction = predict_with_tflite(img_array)
    predicted_class = class_names[np.argmax(prediction)]
    probabilities = {class_names[i]: float(f"{prob:.4f}") for i, prob in enumerate(prediction)}
    
    # Generación de gráfico de barras
    plt.figure(figsize=(6, 4))
    plt.bar(probabilities.keys(), probabilities.values(), color='skyblue')
    plt.title('Probabilidades por clase')
    plt.ylabel('Confianza')
    plt.tight_layout()
    
    graph_path = os.path.join(app.config['UPLOAD_FOLDER'], 'probabilidades.png')
    plt.savefig(graph_path)
    plt.close()
    
    return jsonify({
        'prediction': f'Predicción: {predicted_class.upper()}',
        'image_name': filename,
        'probs': probabilities
    })

if __name__ == '__main__':
        import os
        port = int(os.environ.get("PORT", 5000))
        app.run(host='0.0.0.0', port=port)