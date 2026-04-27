# Extraction Schema - Lab 11

## 1. Яка extraction-задача
Видобування структурованої інформації (загальна тональність, згадані аспекти, переваги, недоліки та оцінка) з україномовних клієнтських відгуків на товари та послуги.

## 2. Які поля у JSON
* `sentiment_type` (string, enum)
* `mentioned_aspects` (array of strings)
* `advantages` (string або null)
* `disadvantages` (string або null)
* `rating_mentioned` (number або null)

## 3. Які поля required
Усі 5 полів є обов'язковими (`required`). Якщо інформація для поля відсутня в тексті, воно все одно має бути присутнім у JSON зі значенням `null` або порожнім масивом `[]`.

## 4. Як виглядає JSON schema
```json
{
  "type": "object",
  "properties": {
    "sentiment_type": {
      "type": "string",
      "enum": ["positive", "negative", "neutral"],
      "description": "Загальна тональність відгуку"
    },
    "mentioned_aspects": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Список аспектів продукту/послуги, що згадуються"
    },
    "advantages": {
      "type": ["string", "null"],
      "description": "Конкретні переваги, згадані у тексті"
    },
    "disadvantages": {
      "type": ["string", "null"],
      "description": "Конкретні недоліки, згадані у тексті"
    },
    "rating_mentioned": {
      "type": ["number", "null"],
      "description": "Числова оцінка, якщо вона явно або неявно вказана в тексті"
    }
  },
  "required": [
    "sentiment_type",
    "mentioned_aspects",
    "advantages",
    "disadvantages",
    "rating_mentioned"
  ],
  "additionalProperties": false
}
```

## 5. Які правила для null / missing values
* Для полів advantages, disadvantages та rating_mentioned використовується тип ["string", "null"] або ["number", "null"]. Це означає, що якщо у відгуку не вказано переваг, недоліків чи числової оцінки, модель зобов'язана повернути значення null (а не пропускати ключ).

* Для mentioned_aspects, якщо аспектів не знайдено, очікується порожній масив [].

* Використовується "additionalProperties": false, що забороняє моделі генерувати власні поля для невідомих значень.

## 6. Які поля найчастіше проблемні
Найчастіше ламаються поля advantages та disadvantages. Модель схильна повертати масив рядків (наприклад, ["погана упаковка", "довга доставка"]), коли недоліків декілька, тоді як схема жорстко вимагає єдиний рядок (string).

## 7. Що repair loop реально виправляє
Repair loop успішно виправляє помилки типу Missing required field (коли модель забула додати поле advantages зі значенням null), а також поодинокі проблеми з парсингом. Додавання оригінального тексту відгуку в repair_prompt виявилося критичним для того, щоб модель могла згенерувати правильний результат з другої спроби.