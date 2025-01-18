from flask import Flask, request, jsonify
import g4f

app = Flask(__name__)

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    text_to_translate = data.get('text')
    target_language = data.get('target_language', 'en')  # По умолчанию перевод на английский

    if not text_to_translate:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Формируем сообщение для модели
        prompt = f"translate the text {text_to_translate} into {target_language} and send only the translation without any comments or additional responses to questions. Perform only the function of a translator."

        # Получаем ответ от модели
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",  # или gpt-4, если доступно
            messages=[{"role": "user", "content": prompt}]
        )

        # Предполагаем, что response - это строка с текстом ответа
        translated_text = response.strip()  # Убираем лишние пробелы

        return jsonify({'translated_text': translated_text}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
