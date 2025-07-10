## https://supabase.com/dashboard/project/nklzooanyyctoqowgimb/api
# JS
import { createClient } from '@supabase/supabase-js'
const supabaseUrl = 'https://nklzooanyyctoqowgimb.supabase.co'
const supabaseKey = process.env.SUPABASE_KEY
const supabase = createClient(supabaseUrl, supabaseKey)


# Connect to your project
All projects have a RESTful endpoint that you can use with your project's API key to query and manage your database. These can be obtained from the API settings.

You can initialize a new Supabase client using the createClient() method. The Supabase client is your entrypoint to the rest of the Supabase functionality and is the easiest way to interact with everything we offer within the Supabase ecosystem.

# Подключитесь к своему проекту
Все проекты имеют конечную точку RESTful, которую вы можете использовать вместе с ключом API вашего проекта для запросов к базе данных и управления ею. Эти ключи можно получить в настройках API.

Вы можете инициализировать новый клиент Supabase с помощью метода createClient(). Клиент Supabase — это ваша точка входа к остальной функциональности Supabase и самый простой способ взаимодействия со всем, что мы предлагаем в экосистеме Supabase.

# JS
import { createClient } from '@supabase/supabase-js'
const supabaseUrl = 'https://nklzooanyyctoqowgimb.supabase.co'
const supabaseKey = process.env.SUPABASE_KEY
const supabase = createClient(supabaseUrl, supabaseKey)


# Authentication
Supabase works through a mixture of JWT and Key auth.

If no Authorization header is included, the API will assume that you are making a request with an anonymous user.

If an Authorization header is included, the API will "switch" to the role of the user making the request. See the User Management section for more details.

We recommend setting your keys as Environment Variables.

# Аутентификация
Supabase использует комбинацию JWT и аутентификации по ключам.

Если заголовок Authorization не указан, API будет считать, что вы отправляете запрос от имени анонимного пользователя.

Если заголовок Authorization указан, API «переключится» на роль пользователя, отправившего запрос. Подробнее см. в разделе «Управление пользователями».

Мы рекомендуем настроить ключи как переменные среды.

# Client API Keys
Client keys allow "anonymous access" to your database, until the user has logged in. After logging in the keys will switch to the user's own login token.

In this documentation, we will refer to the key using the name SUPABASE_KEY.

We have provided you a Client Key to get started. You will soon be able to add as many keys as you like. You can find the anon key in the API Settings page.

# Клиентские ключи API
Клиентские ключи обеспечивают «анонимный доступ» к вашей базе данных до тех пор, пока пользователь не войдет в систему. После входа в систему ключи будут использовать собственный токен пользователя.

В этой документации мы будем использовать для обозначения ключа имя SUPABASE_KEY.

Мы предоставили вам клиентский ключ для начала работы. Скоро вы сможете добавлять столько ключей, сколько захотите. Анонимный ключ можно найти на странице настроек API.

# CLIENT API KEY
const SUPABASE_KEY = 'SUPABASE_CLIENT_API_KEY'

# Example usage
const SUPABASE_URL = "https://nklzooanyyctoqowgimb.supabase.co"
const supabase = createClient(SUPABASE_URL, process.env.SUPABASE_KEY);

# Service Keys
Service keys have FULL access to your data, bypassing any security policies. Be VERY careful where you expose these keys. They should only be used on a server and never on a client or browser.

In this documentation, we will refer to the key using the name SERVICE_KEY.

We have provided you with a Service Key to get started. Soon you will be able to add as many keys as you like. You can find the service_role in the API Settings page.

# Сервисные ключи
Сервисные ключи предоставляют ПОЛНЫЙ доступ к вашим данным, обходя любые политики безопасности. Будьте ОЧЕНЬ осторожны, предоставляя эти ключи. Их следует использовать только на сервере, а не на клиенте или в браузере.

В этой документации мы будем использовать для ключа имя SERVICE_KEY.

Мы предоставили вам сервисный ключ для начала работы. Скоро вы сможете добавлять столько ключей, сколько захотите. Роль service_role можно найти на странице настроек API.

# SERVICE KEY
const SERVICE_KEY = 'SUPABASE_SERVICE_KEY'

# Example usage
const SUPABASE_URL = "https://nklzooanyyctoqowgimb.supabase.co"
const supabase = createClient(SUPABASE_URL, process.env.SERVICE_KEY);


# User Management
Supabase makes it easy to manage your users.

Supabase assigns each user a unique ID. You can reference this ID anywhere in your database. For example, you might create a profiles table references the user using a user_id field.

Supabase already has built in the routes to sign up, login, and log out for managing users in your apps and websites.

Sign up
Allow your users to sign up and create a new account.

After they have signed up, all interactions using the Supabase JS client will be performed as "that user".

User signup
let { data, error } = await supabase.auth.signUp({
  email: 'someone@email.com',
  password: 'CaNmusBwjaftySImFjwz'
})
Log in with Email/Password
If an account is created, users can login to your app.

After they have logged in, all interactions using the Supabase JS client will be performed as "that user".

User login
let { data, error } = await supabase.auth.signInWithPassword({
  email: 'someone@email.com',
  password: 'CaNmusBwjaftySImFjwz'
})
Log in with Magic Link via Email
Send a user a passwordless link which they can use to redeem an access_token.

After they have clicked the link, all interactions using the Supabase JS client will be performed as "that user".

User login
let { data, error } = await supabase.auth.signInWithOtp({
  email: 'someone@email.com'
})
Sign Up with Phone/Password
A phone number can be used instead of an email as a primary account confirmation mechanism.

The user will receive a mobile OTP via sms with which they can verify that they control the phone number.

You must enter your own twilio credentials on the auth settings page to enable sms confirmations.

Phone Signup
let { data, error } = await supabase.auth.signUp({
  phone: '+13334445555',
  password: 'some-password'
})
Login via SMS OTP
SMS OTPs work like magic links, except you have to provide an interface for the user to verify the 6 digit number they receive.

You must enter your own twilio credentials on the auth settings page to enable SMS-based Logins.

Phone Login
let { data, error } = await supabase.auth.signInWithOtp({
  phone: '+13334445555'
})
Verify an SMS OTP
Once the user has received the OTP, have them enter it in a form and send it for verification

You must enter your own twilio credentials on the auth settings page to enable SMS-based OTP verification.

Verify Pin
let { data, error } = await supabase.auth.verifyOtp({
  phone: '+13334445555',
  token: '123456',
  type: 'sms'
})
Log in with Third Party OAuth
Users can log in with Third Party OAuth like Google, Facebook, GitHub, and more. You must first enable each of these in the Auth Providers settings here .

View all the available Third Party OAuth providers

After they have logged in, all interactions using the Supabase JS client will be performed as "that user".

Generate your Client ID and secret from: Google, GitHub, GitLab, Facebook, Bitbucket.

Third Party Login
let { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'github'
})
User
Get the JSON object for the logged in user.

Get User
const { data: { user } } = await supabase.auth.getUser()
Forgotten Password Email
Sends the user a log in link via email. Once logged in you should direct the user to a new password form. And use "Update User" below to save the new password.

Password Recovery
let { data, error } = await supabase.auth.resetPasswordForEmail(email)
Update User
Update the user with a new email or password. Each key (email, password, and data) is optional

Update User
const { data, error } = await supabase.auth.updateUser({
  email: "new@email.com",
  password: "new-password",
  data: { hello: 'world' }
})
Log out
After calling log out, all interactions using the Supabase JS client will be "anonymous".

User logout
let { error } = await supabase.auth.signOut()
Send a User an Invite over Email
Send a user a passwordless link which they can use to sign up and log in.

After they have clicked the link, all interactions using the Supabase JS client will be performed as "that user".

This endpoint requires you use the service_role_key when initializing the client, and should only be invoked from the server, never from the client.

Invite User
let { data, error } = await supabase.auth.admin.inviteUserByEmail('someone@email.com')

# Управление пользователями
## Supabase упрощает управление пользователями.

Supabase присваивает каждому пользователю уникальный идентификатор. Вы можете ссылаться на этот идентификатор в любом месте базы данных. Например, можно создать таблицу профилей, которая будет ссылаться на пользователя с помощью поля user_id.

## В Supabase уже встроены маршруты для регистрации, входа и выхода из системы для управления пользователями в ваших приложениях и на веб-сайтах.

# Регистрация
Разрешите пользователям регистрироваться и создавать новые учётные записи.

После регистрации все взаимодействия с JS-клиентом Supabase будут выполняться от имени этого пользователя.

## Регистрация пользователя
let { data, error } = await supabase.auth.signUp({
email: 'someone@email.com',
password: 'CaNmusBwjaftySImFjwz'
})

Войти с помощью адреса электронной почты/пароля
После создания учётной записи пользователи смогут войти в ваше приложение.

После входа в систему все взаимодействия с клиентом Supabase JS будут выполняться от имени «этого пользователя».

## Вход пользователя
let { data, error } = await supabase.auth.signInWithPassword({
email: 'someone@email.com',
password: 'CaNmusBwjaftySImFjwz'
})

## Войти по волшебной ссылке по электронной почте
Отправить пользователю ссылку без пароля, по которой он сможет активировать access_token.

После перехода по ссылке все взаимодействия с клиентом Supabase JS будут выполняться от имени «этого пользователя».

Вход пользователя
let { data, error } = await supabase.auth.signInWithOtp({
email: 'someone@email.com'
})


## Регистрация по телефону/паролю
В качестве основного способа подтверждения учётной записи вместо адреса электронной почты можно использовать номер телефона.

Пользователь получит мобильный одноразовый пароль по SMS, с помощью которого он сможет подтвердить, что контролирует номер телефона.

Чтобы включить SMS-подтверждения, необходимо ввести свои учётные данные Twilio на странице настроек авторизации.

Регистрация по телефону
let { data, error } = await supabase.auth.signUp({
phone: '+13334445555',
password: 'some-password'
})


## Вход через SMS-одноразовый пароль
SMS-одноразовые пароли работают как волшебные ссылки, за исключением того, что пользователю необходимо предоставить интерфейс для проверки полученного шестизначного номера.

Чтобы включить вход через SMS-пароль, необходимо ввести свои учётные данные Twilio на странице настроек авторизации.

Вход по телефону
let { data, error } = await supabase.auth.signInWithOtp({
phone: '+13334445555'
})

## Проверка одноразового пароля из SMS
После того, как пользователь получит одноразовый пароль, попросите его ввести его в форму и отправить на проверку.

Чтобы включить проверку одноразового пароля по SMS, необходимо ввести свои учетные данные Twilio на странице настроек авторизации.

Подтверждение PIN-кода
let { data, error } = await supabase.auth.verifyOtp({
phone: '+13334445555',
token: '123456',
type: 'sms'
})


## Вход с использованием стороннего OAuth
Пользователи могут входить с использованием стороннего OAuth, например, Google, Facebook, GitHub и других. Необходимо сначала включить каждый из этих сервисов в настройках поставщиков авторизации.

Посмотреть всех доступных сторонних поставщиков OAuth

После входа в систему все взаимодействия с использованием клиента Supabase JS будут выполняться от имени этого пользователя.

Сгенерируйте идентификатор клиента и секретный ключ из следующих источников: Google, GitHub, GitLab, Facebook, Bitbucket.

Вход через сторонний сервис
let { data, error } = await supabase.auth.signInWithOAuth({
provider: 'github'
})
Пользователь
Получить JSON-объект для вошедшего в систему пользователя.

Получить пользователя
const { data: { user } } = await supabase.auth.getUser()
Электронное письмо о забытом пароле
Отправляет пользователю ссылку для входа по электронной почте. После входа в систему необходимо перенаправить пользователя на форму ввода нового пароля. Для сохранения нового пароля используйте кнопку «Обновить пользователя» ниже.

Восстановление пароля
let { data, error} = await supabase.auth.resetPasswordForEmail(email)
Обновить пользователя
Обновить адрес электронной почты или пароль пользователя. Каждый ключ (email, password и data) необязателен.

Обновить пользователя
const { data, error} = await supabase.auth.updateUser({
email: "new@email.com",
password: "new-password",
data: { hello: 'world' }
})
Выход
После вызова log out все взаимодействия с использованием JS-клиента Supabase будут «анонимными».

Выход пользователя
let { error} = await supabase.auth.signOut()
Отправить пользователю приглашение по электронной почте
Отправить пользователю ссылку без пароля, по которой он сможет зарегистрироваться и войти в систему.

После перехода по ссылке все взаимодействия с использованием JS-клиента Supabase будут выполняться от имени этого пользователя.

Эта конечная точка требует использования service_role_key при инициализации клиента и должна вызываться только с сервера, а не с клиента.

Пригласить пользователя
let { data, error } = await supabase.auth.admin.inviteUserByEmail('someone@email.com')

# Introduction
All views and tables in the public schema and accessible by the active database role for a request are available for querying.

Non-exposed tables
If you don't want to expose tables in your API, simply add them to a different schema (not the public schema).

Generating types
Docs
Supabase APIs are generated from your database, which means that we can use database introspection to generate type-safe API definitions.

You can generate types from your database either through the Supabase CLI, or by downloading the types file via the button on the right and importing it in your application within src/index.ts.


Generate and download types

Remember to re-generate and download this file as you make changes to your tables.

GraphQL vs Supabase
If you have a GraphQL background, you might be wondering if you can fetch your data in a single round-trip. The answer is yes!

The syntax is very similar. This example shows how you might achieve the same thing with Apollo GraphQL and Supabase.


Still want GraphQL?
If you still want to use GraphQL, you can. Supabase provides you with a full Postgres database, so as long as your middleware can connect to the database then you can still use the tools you love. You can find the database connection details in the settings.

With Apollo GraphQL
const { loading, error, data } = useQuery(gql`
  query GetDogs {
    dogs {
      id
      breed
      owner {
        id
        name
      }
    }
  }
`)
With Supabase
const { data, error } = await supabase
  .from('dogs')
  .select(`
      id, breed,
      owner (id, name)
  `)


# Введение
Все представления и таблицы в общедоступной схеме, доступные активной роли базы данных для запроса, доступны для выполнения запросов.

Неоткрытые таблицы
Если вы не хотите открывать таблицы в своём API, просто добавьте их в другую схему (не общедоступную).

Генерация типов
Документация
API Supabase генерируются из вашей базы данных, что означает, что мы можем использовать интроспекцию базы данных для создания типобезопасных определений API.

Вы можете генерировать типы из вашей базы данных либо через интерфейс командной строки Supabase, либо загрузив файл типов с помощью кнопки справа и импортировав его в своё приложение в src/index.ts.

Генерация и загрузка типов

Не забывайте повторно генерировать и загружать этот файл при внесении изменений в таблицы.

GraphQL против Supabase
Если у вас есть опыт работы с GraphQL, вы, возможно, задаётесь вопросом, можно ли извлечь данные за один цикл. Ответ — да!

Синтаксис очень похож. Этот пример показывает, как можно добиться того же результата с помощью Apollo GraphQL и Supabase.

Всё ещё нужен GraphQL?
Если вы всё ещё хотите использовать GraphQL, это возможно. Supabase предоставляет вам полноценную базу данных Postgres, поэтому, если ваше промежуточное ПО может подключиться к базе данных, вы сможете использовать любимые инструменты. Параметры подключения к базе данных можно найти в настройках.

С Apollo GraphQL
const { loading, error, data } = useQuery(gql`
query GetDogs {
dogs {
id
breed
owner {
id
name
}
}
}
`)


С Supabase
const { data, error } = await supabase
.from('dogs')
.select(`
id, breed,
owner (id, name)
`)


# forecasts
Description
Click to edit.

Cancel

Save
Column
id
Required
Type
number
Format
bigint
Description
Click to edit.

Cancel

Save
Select id
let { data: forecasts, error } = await supabase
  .from('forecasts')
  .select('id')
Column
sku_id
Required
Type
string
Format
character varying
Description
Click to edit.

Cancel

Save
Select sku_id
let { data: forecasts, error } = await supabase
  .from('forecasts')
  .select('sku_id')
Column
forecast_date
Required
Type
string
Format
date
Description
Click to edit.

Cancel

Save
Select forecast_date
let { data: forecasts, error } = await supabase
  .from('forecasts')
  .select('forecast_date')
Column
predicted_sales
Required
Type
number
Format
integer
Description
Click to edit.

Cancel

Save
Select predicted_sales
let { data: forecasts, error } = await supabase
  .from('forecasts')
  .select('predicted_sales')
Column
confidence_score
Optional
Type
number
Format
double precision
Description
Click to edit.

Cancel

Save
Select confidence_score
let { data: forecasts, error } = await supabase
  .from('forecasts')
  .select('confidence_score')
Column
key_factors
Optional
Type
Format
text[]
Description
Click to edit.

Cancel

Save
Select key_factors
let { data: forecasts, error } = await supabase
  .from('forecasts')
  .select('key_factors')
Column
created_at
Optional
Type
string
Format
timestamp without time zone
Description
Click to edit.

Cancel

Save
Select created_at
let { data: forecasts, error } = await supabase
  .from('forecasts')
  .select('created_at')
Read rows
To read rows in forecasts, use the select method.

Learn more

Read all rows
let { data: forecasts, error } = await supabase
  .from('forecasts')
  .select('*')
Read specific columns
let { data: forecasts, error } = await supabase
  .from('forecasts')
  .select('some_column,other_column')
Read referenced tables
let { data: forecasts, error } = await supabase
  .from('forecasts')
  .select(`
    some_column,
    other_table (
      foreign_key
    )
  `)
With pagination
let { data: forecasts, error } = await supabase
  .from('forecasts')
  .select('*')
  .range(0, 9)
Filtering
Supabase provides a wide range of filters.

Learn more

With filtering
let { data: forecasts, error } = await supabase
  .from('forecasts')
  .select("*")

  // Filters
  .eq('column', 'Equal to')
  .gt('column', 'Greater than')
  .lt('column', 'Less than')
  .gte('column', 'Greater than or equal to')
  .lte('column', 'Less than or equal to')
  .like('column', '%CaseSensitive%')
  .ilike('column', '%CaseInsensitive%')
  .is('column', null)
  .in('column', ['Array', 'Values'])
  .neq('column', 'Not equal to')

  // Arrays
  .contains('array_column', ['array', 'contains'])
  .containedBy('array_column', ['contained', 'by'])

  // Logical operators
  .not('column', 'like', 'Negate filter')
  .or('some_column.eq.Some value, other_column.eq.Other value')
Insert rows
insert lets you insert into your tables. You can also insert in bulk and do UPSERT.

insert will also return the replaced values for UPSERT.

Learn more

Insert a row
const { data, error } = await supabase
  .from('forecasts')
  .insert([
    { some_column: 'someValue', other_column: 'otherValue' },
  ])
  .select()
Insert many rows
const { data, error } = await supabase
  .from('forecasts')
  .insert([
    { some_column: 'someValue' },
    { some_column: 'otherValue' },
  ])
  .select()
Upsert matching rows
const { data, error } = await supabase
  .from('forecasts')
  .upsert({ some_column: 'someValue' })
  .select()
Update rows
update lets you update rows. update will match all rows by default. You can update specific rows using horizontal filters, e.g. eq, lt, and is.

update will also return the replaced values for UPDATE.

Learn more

Update matching rows
const { data, error } = await supabase
  .from('forecasts')
  .update({ other_column: 'otherValue' })
  .eq('some_column', 'someValue')
  .select()
Delete rows
delete lets you delete rows. delete will match all rows by default, so remember to specify your filters!

Learn more

Delete matching rows
const { error } = await supabase
  .from('forecasts')
  .delete()
  .eq('some_column', 'someValue')
Subscribe to changes
Supabase provides realtime functionality and broadcasts database changes to authorized users depending on Row Level Security (RLS) policies.

Learn more

Subscribe to all events
const forecasts = supabase.channel('custom-all-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'forecasts' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to inserts
const forecasts = supabase.channel('custom-insert-channel')
  .on(
    'postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'forecasts' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to updates
const forecasts = supabase.channel('custom-update-channel')
  .on(
    'postgres_changes',
    { event: 'UPDATE', schema: 'public', table: 'forecasts' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to deletes
const forecasts = supabase.channel('custom-delete-channel')
  .on(
    'postgres_changes',
    { event: 'DELETE', schema: 'public', table: 'forecasts' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to specific rows
const forecasts = supabase.channel('custom-filter-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'forecasts', filter: 'column_name=eq.someValue' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()


# JavaScript
Bash
sales_data
Description
Click to edit.

Cancel

Save
Column
id
Required
Type
number
Format
bigint
Description
Click to edit.

Cancel

Save
Select id
let { data: sales_data, error } = await supabase
  .from('sales_data')
  .select('id')
Column
date
Required
Type
string
Format
date
Description
Click to edit.

Cancel

Save
Select date
let { data: sales_data, error } = await supabase
  .from('sales_data')
  .select('date')
Column
sku_id
Required
Type
string
Format
character varying
Description
Click to edit.

Cancel

Save
Select sku_id
let { data: sales_data, error } = await supabase
  .from('sales_data')
  .select('sku_id')
Column
sales_quantity
Required
Type
number
Format
integer
Description
Click to edit.

Cancel

Save
Select sales_quantity
let { data: sales_data, error } = await supabase
  .from('sales_data')
  .select('sales_quantity')
Column
avg_temp
Required
Type
number
Format
double precision
Description
Click to edit.

Cancel

Save
Select avg_temp
let { data: sales_data, error } = await supabase
  .from('sales_data')
  .select('avg_temp')
Column
created_at
Optional
Type
string
Format
timestamp without time zone
Description
Click to edit.

Cancel

Save
Select created_at
let { data: sales_data, error } = await supabase
  .from('sales_data')
  .select('created_at')
Read rows
To read rows in sales_data, use the select method.

Learn more

Read all rows
let { data: sales_data, error } = await supabase
  .from('sales_data')
  .select('*')
Read specific columns
let { data: sales_data, error } = await supabase
  .from('sales_data')
  .select('some_column,other_column')
Read referenced tables
let { data: sales_data, error } = await supabase
  .from('sales_data')
  .select(`
    some_column,
    other_table (
      foreign_key
    )
  `)
With pagination
let { data: sales_data, error } = await supabase
  .from('sales_data')
  .select('*')
  .range(0, 9)
Filtering
Supabase provides a wide range of filters.

Learn more

With filtering
let { data: sales_data, error } = await supabase
  .from('sales_data')
  .select("*")

  // Filters
  .eq('column', 'Equal to')
  .gt('column', 'Greater than')
  .lt('column', 'Less than')
  .gte('column', 'Greater than or equal to')
  .lte('column', 'Less than or equal to')
  .like('column', '%CaseSensitive%')
  .ilike('column', '%CaseInsensitive%')
  .is('column', null)
  .in('column', ['Array', 'Values'])
  .neq('column', 'Not equal to')

  // Arrays
  .contains('array_column', ['array', 'contains'])
  .containedBy('array_column', ['contained', 'by'])

  // Logical operators
  .not('column', 'like', 'Negate filter')
  .or('some_column.eq.Some value, other_column.eq.Other value')
Insert rows
insert lets you insert into your tables. You can also insert in bulk and do UPSERT.

insert will also return the replaced values for UPSERT.

Learn more

Insert a row
const { data, error } = await supabase
  .from('sales_data')
  .insert([
    { some_column: 'someValue', other_column: 'otherValue' },
  ])
  .select()
Insert many rows
const { data, error } = await supabase
  .from('sales_data')
  .insert([
    { some_column: 'someValue' },
    { some_column: 'otherValue' },
  ])
  .select()
Upsert matching rows
const { data, error } = await supabase
  .from('sales_data')
  .upsert({ some_column: 'someValue' })
  .select()
Update rows
update lets you update rows. update will match all rows by default. You can update specific rows using horizontal filters, e.g. eq, lt, and is.

update will also return the replaced values for UPDATE.

Learn more

Update matching rows
const { data, error } = await supabase
  .from('sales_data')
  .update({ other_column: 'otherValue' })
  .eq('some_column', 'someValue')
  .select()
Delete rows
delete lets you delete rows. delete will match all rows by default, so remember to specify your filters!

Learn more

Delete matching rows
const { error } = await supabase
  .from('sales_data')
  .delete()
  .eq('some_column', 'someValue')
Subscribe to changes
Supabase provides realtime functionality and broadcasts database changes to authorized users depending on Row Level Security (RLS) policies.

Learn more

Subscribe to all events
const salesData = supabase.channel('custom-all-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'sales_data' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to inserts
const salesData = supabase.channel('custom-insert-channel')
  .on(
    'postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'sales_data' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to updates
const salesData = supabase.channel('custom-update-channel')
  .on(
    'postgres_changes',
    { event: 'UPDATE', schema: 'public', table: 'sales_data' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to deletes
const salesData = supabase.channel('custom-delete-channel')
  .on(
    'postgres_changes',
    { event: 'DELETE', schema: 'public', table: 'sales_data' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to specific rows
const salesData = supabase.channel('custom-filter-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'sales_data', filter: 'column_name=eq.someValue' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()


# JavaScript
Bash
user_inputs
Description
Click to edit.

Cancel

Save
Column
id
Required
Type
number
Format
bigint
Description
Click to edit.

Cancel

Save
Select id
let { data: user_inputs, error } = await supabase
  .from('user_inputs')
  .select('id')
Column
session_id
Required
Type
string
Format
character varying
Description
Click to edit.

Cancel

Save
Select session_id
let { data: user_inputs, error } = await supabase
  .from('user_inputs')
  .select('session_id')
Column
input_type
Required
Type
string
Format
character varying
Description
Click to edit.

Cancel

Save
Select input_type
let { data: user_inputs, error } = await supabase
  .from('user_inputs')
  .select('input_type')
Column
sku_id
Required
Type
string
Format
character varying
Description
Click to edit.

Cancel

Save
Select sku_id
let { data: user_inputs, error } = await supabase
  .from('user_inputs')
  .select('sku_id')
Column
start_date
Optional
Type
string
Format
date
Description
Click to edit.

Cancel

Save
Select start_date
let { data: user_inputs, error } = await supabase
  .from('user_inputs')
  .select('start_date')
Column
end_date
Optional
Type
string
Format
date
Description
Click to edit.

Cancel

Save
Select end_date
let { data: user_inputs, error } = await supabase
  .from('user_inputs')
  .select('end_date')
Column
discount_percent
Optional
Type
number
Format
double precision
Description
Click to edit.

Cancel

Save
Select discount_percent
let { data: user_inputs, error } = await supabase
  .from('user_inputs')
  .select('discount_percent')
Column
new_price
Optional
Type
number
Format
double precision
Description
Click to edit.

Cancel

Save
Select new_price
let { data: user_inputs, error } = await supabase
  .from('user_inputs')
  .select('new_price')
Column
created_at
Optional
Type
string
Format
timestamp without time zone
Description
Click to edit.

Cancel

Save
Select created_at
let { data: user_inputs, error } = await supabase
  .from('user_inputs')
  .select('created_at')
Read rows
To read rows in user_inputs, use the select method.

Learn more

Read all rows
let { data: user_inputs, error } = await supabase
  .from('user_inputs')
  .select('*')
Read specific columns
let { data: user_inputs, error } = await supabase
  .from('user_inputs')
  .select('some_column,other_column')
Read referenced tables
let { data: user_inputs, error } = await supabase
  .from('user_inputs')
  .select(`
    some_column,
    other_table (
      foreign_key
    )
  `)
With pagination
let { data: user_inputs, error } = await supabase
  .from('user_inputs')
  .select('*')
  .range(0, 9)
Filtering
Supabase provides a wide range of filters.

Learn more

With filtering
let { data: user_inputs, error } = await supabase
  .from('user_inputs')
  .select("*")

  // Filters
  .eq('column', 'Equal to')
  .gt('column', 'Greater than')
  .lt('column', 'Less than')
  .gte('column', 'Greater than or equal to')
  .lte('column', 'Less than or equal to')
  .like('column', '%CaseSensitive%')
  .ilike('column', '%CaseInsensitive%')
  .is('column', null)
  .in('column', ['Array', 'Values'])
  .neq('column', 'Not equal to')

  // Arrays
  .contains('array_column', ['array', 'contains'])
  .containedBy('array_column', ['contained', 'by'])

  // Logical operators
  .not('column', 'like', 'Negate filter')
  .or('some_column.eq.Some value, other_column.eq.Other value')
Insert rows
insert lets you insert into your tables. You can also insert in bulk and do UPSERT.

insert will also return the replaced values for UPSERT.

Learn more

Insert a row
const { data, error } = await supabase
  .from('user_inputs')
  .insert([
    { some_column: 'someValue', other_column: 'otherValue' },
  ])
  .select()
Insert many rows
const { data, error } = await supabase
  .from('user_inputs')
  .insert([
    { some_column: 'someValue' },
    { some_column: 'otherValue' },
  ])
  .select()
Upsert matching rows
const { data, error } = await supabase
  .from('user_inputs')
  .upsert({ some_column: 'someValue' })
  .select()
Update rows
update lets you update rows. update will match all rows by default. You can update specific rows using horizontal filters, e.g. eq, lt, and is.

update will also return the replaced values for UPDATE.

Learn more

Update matching rows
const { data, error } = await supabase
  .from('user_inputs')
  .update({ other_column: 'otherValue' })
  .eq('some_column', 'someValue')
  .select()
Delete rows
delete lets you delete rows. delete will match all rows by default, so remember to specify your filters!

Learn more

Delete matching rows
const { error } = await supabase
  .from('user_inputs')
  .delete()
  .eq('some_column', 'someValue')
Subscribe to changes
Supabase provides realtime functionality and broadcasts database changes to authorized users depending on Row Level Security (RLS) policies.

Learn more

Subscribe to all events
const userInputs = supabase.channel('custom-all-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'user_inputs' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to inserts
const userInputs = supabase.channel('custom-insert-channel')
  .on(
    'postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'user_inputs' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to updates
const userInputs = supabase.channel('custom-update-channel')
  .on(
    'postgres_changes',
    { event: 'UPDATE', schema: 'public', table: 'user_inputs' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to deletes
const userInputs = supabase.channel('custom-delete-channel')
  .on(
    'postgres_changes',
    { event: 'DELETE', schema: 'public', table: 'user_inputs' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()
Subscribe to specific rows
const userInputs = supabase.channel('custom-filter-channel')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'user_inputs', filter: 'column_name=eq.someValue' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()


######################
