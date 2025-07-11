# Patch — поддержка `predicted_sales` в ответе бэкенда

Цель: фронтенд должен корректно отображать прогнозы, когда бэкенд отдает поле **`predicted_sales`** (новое имя). При этом совместимость со старыми версиями (`predicted_units`) сохраняется, а расчёт метрик перестаёт давать `null`.

---

## 1. Обновить типы
Файл `src/types/Forecast.ts` или аналогичный, где описана точка прогноза.

```ts
export interface ForecastPoint {
  date: string;            // ISO-дата
  predicted_sales: number; // новое поле
  confidence: number;
  // для совместимости со старыми ответами
  predicted_units?: number;
  sales?: number;          // встречается в mock-режиме
}
```

## 2. Нормализация ответа API
Файл `src/utils/useApi.ts` **или** компонент `ForecastPanel.tsx`, где происходит запрос `/forecast`.

```ts
const raw = response.data.predictions;

const points = raw.map((p: any) => {
  const sales = p.predicted_sales ?? p.predicted_units ?? p.sales ?? 0;
  return {
    date: p.date,
    sales,          // удобное унифицированное имя внутри фронта
    confidence: p.confidence,
  };
});
```

> Замените остальные обращения к `predicted_units`/`predicted_sales` на `sales`.

## 3. Пересчёт метрик
Пример кода расчёта (где-то в `ForecastPanel`):

```ts
const total = points.reduce((sum, p) => sum + p.sales, 0);
const avgWeeklySales = +(total / points.length).toFixed(1);

setMetrics({
  avgWeeklySales,
  trend: calcTrend(points),  // ваша функция тренда
  accuracy: calcAccuracy(points),
});
```

Если функции `calcTrend` и `calcAccuracy` напрямую использовали `predicted_units` — переключите их на `sales`.

## 4. Отправка периода
Убедитесь, что в тело запроса уходит выбранный период строкой `"7" | "14" | "30"`.

```ts
await api.post("/forecast", {
  sku_id,
  period: selectedPeriod.toString(),
  context,
});
```

## 5. Перезапуск
```bash
npm install   # если нужно
npm run dev   # локальная разработка
npm run build # production-сборка
```

После этого:
* При выборе периода 7/14/30 дней UI получит ровно столько точек.
* Метрики перестанут быть `null`.
* Старый бэкенд (с `predicted_units`) всё ещё будет работать.
