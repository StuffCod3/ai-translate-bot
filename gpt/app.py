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
        prompt = f"You act as a translator, spelling corrector and editor. I will speak to you in any language and you will detect the language, translate it and answer in the corrected and improved version of my text. Please translate my text, improving the language to a more literary version in {target_language}. Make sure that {target_language} version is grammatically and semantically correct. Keep the original meaning the same. Only reply the correction, the improvements and nothing else, do not write explanations. My text: {text_to_translate}"

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
