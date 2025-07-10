# Проверка доступности данных через REST

Перейти во вкладку Settings → API и скопировать:

Project URL (например https://nklzooanyyctoqowgimb.supabase.co)

anon public key


# API SETTINGS
## https://supabase.com/dashboard/project/nklzooanyyctoqowgimb/settings/api


URL=https://nklzooanyyctoqowgimb.supabase.co

# Проверить GET-запрос к таблице sales_data (Postman, curl или fetch):

curl -H "apikey: <anon_key>" \
     -H "Authorization: Bearer <anon_key>" \
     "https://nklzooanyyctoqowgimb.supabase.co/rest/v1/sales_data?limit=1"


curl -H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5rbHpvb2FueXljdG9xb3dnaW1iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA0NDM1MjAsImV4cCI6MjA2NjAxOTUyMH0.MMz8exqmL0nQ7kTqVV9Xqzh-qR0fDi5Xl3vSafNoDA0" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5rbHpvb2FueXljdG9xb3dnaW1iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA0NDM1MjAsImV4cCI6MjA2NjAxOTUyMH0.MMz8exqmL0nQ7kTqVV9Xqzh-qR0fDi5Xl3vSafNoDA0" \
     "https://nklzooanyyctoqowgimb.supabase.co/rest/v1/sales_data?limit=1"


[]aaaaa@aaaaa-GF63-Thin-9SCXR:~/AI-TUTORIALS/khabarovsk-server-dbase$ ^C
aaaaa@aaaaa-GF63-Thin-9SCXR:~/AI-TUTORIALS/khabarovsk-server-dbase$


# Ожидаемый ответ: [] (пустой массив) — значит таблица доступна и пока пуста.
Неожиданный ответ: {"message":"permission denied"} — RLS политика не активировалась; проверьте, включён ли Enable RLS.

# Шаг 1.4 Импорт мок-данных для теста
Во вкладке Table Editor выбрать sales_data → Insert Row.

Ввести одну строку вручную или использовать Bulk Import:

Меню Import Data → загрузить sales_data_mock.csv.

Нажать Import → увидеть уведомление Rows imported: 52.
