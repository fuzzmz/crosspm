<a class="mk-toclify" id="table-of-contents"></a>

# Table of Contents
- [Как запретить в конфиге рекурсивное выкачивание пакетов?](#)
- [CrossPM вылетает с ошибкой при поиске в репозитории с анонимным доступом (type: artifactory-aql)](#crosspm-type-artifactory-aql)
- [Как отфильтровать пакеты, чтобы выбирались только БЕЗ feature в версии?](#feature)
- [А как отфильтровать пакеты, чтобы выбирались ТОЛЬКО feature версии?](#feature)
- [Как скачать два пакеты с разной версией, но один именем?](#)
- [Один модуль ищется 5 минут, как ускорить поиск? (type: artifactory)](#5-type-artifactory)
- [Как вынести пароль из файла конфигурации?](#)
- [Как сделать проверку что все используемые пакеты имеют одинаковую версию? Например, что все используют последнюю версию openssl?](#openssl)
- [Хочу использовать кеш, но crosspm странно себя ведет - берет кеш пакета с другой версией?](#crosspm)
- [Не хочу создавать dependencies-файл, хочу указать сразу в команде crosspm список пакетов](#content)
- [Как просто и безопасно передавать учётные данные в рамках crosspm](#creds)

Frequently Asked Questions
==========================

<a class="mk-toclify" id=""></a>
## Как запретить в конфиге рекурсивное выкачивание пакетов?
Можно задать неправильные имена файлов dependencies, тогда он не найдет их и не пойдет глубже
```yaml
cpm:
dependencies: no-dependencies.txt
dependencies-lock: no-dependencies.txt.lock
```
И вызывать с указанием правильного файла:
```bash
crosspm download --depslock-path=./dependencies.txt.lock
```

<a class="mk-toclify" id="crosspm-type-artifactory-aql"></a>
## CrossPM вылетает с ошибкой при поиске в репозитории с анонимным доступом (type: artifactory-aql)
Это ограничение запросов AQL в Artifactory - их возможно использовать только с авторизацией. Добавьте в конфиг любые учетные данные для доступа к этим репозиториям

<a class="mk-toclify" id="feature"></a>
## Как отфильтровать пакеты, чтобы выбирались только БЕЗ feature в версии?
Если формат версии в конфиге определен так:
```yaml
columns:
version: "{int}.{int}.{int}[-{str}]"
```
то в dependencies можно указать, что необязательной части шаблона быть не должно. Для этого нужно добавить разделитель из необязательной части в конце маски версии. Несколько вариантов для примера:
```
PackageName    *-         R14.1    >=snapshot
PackageName    *.*.*-     R14.1    >=snapshot
PackageName    14.*.*-    R14.1    >=snapshot
```

<a class="mk-toclify" id="feature"></a>
## А как отфильтровать пакеты, чтобы выбирались ТОЛЬКО feature версии?
Если формат версии в конфиге определен так:
```yaml
columns:
version: "{int}.{int}.{int}[-{str}]"
```
то в dependencies можно указать, что необязательная часть шаблона должна быть. Для этого нужно добавить эту необязательную часть в конце маски версии. В таком случае CrossPM не будет брать версии без feature. Несколько вариантов для примера:
```
Agent    *-*            R14.1    >=snapshot
Agent    *-develop      R14.1    >=snapshot
Agent    *.*.*-*        R14.1    >=snapshot
Agent    14.*.*-*       R14.1    >=snapshot
Agent    14.*.*-CERT*   R14.1    >=snapshot
```

<a class="mk-toclify" id=""></a>
## Как скачать два пакеты с разной версией, но один именем?

Нужно создать "псевдоуникальное имя пакета". Пример файла **dependencies.txt.lock**
```
PackageRelease17 Package 17.0.*
PackageRelease161 Package 16.1.*
OtherPackage OtherPackage *
```
И добавить в конфиг строки

```yaml
columns: "*uniquename, package, version" # Указание в какой колонке указано имя пакета

output: # Для упрощения дебага в stdout
tree:
- uniquename: 25
- version: 0
```


<a class="mk-toclify" id="5-type-artifactory"></a>
## Один модуль ищется 5 минут, как ускорить поиск? (type: artifactory)
Данная проблема могла наблюдаться в адаптере **artifactory**, нужно поменять его на **artifactory-aql**
```yaml
type: artifactory-aql
```

<a class="mk-toclify" id=""></a>
## Как вынести пароль из файла конфигурации?
С помощью [разделения на два файла конфигурации и использования import](config/IMPORT)


<a class="mk-toclify" id="openssl"></a>
## Как сделать проверку что все используемые пакеты имеют одинаковую версию? Например, что все используют последнюю версию openssl?

Если нужно проверить, что все пакеты используют одну версию пакетов, **но** загрузить только файлы, указанные непосредственно в **dependencies.txt**, можно поступить следующим образом:
1. [Разделить файлы конфигурации](config/IMPORT) на **crosspm.main.yaml**, **crosspm.download.yaml**, **crosspm.lock.yaml**
2. В **lock**-конфигурации указать существующий **dependencies.txt.lock**
3. В **download**-конфигурации указать НЕ существующий **no-dependencies.txt.lock**
4. Запустить crosspm с указанием разных конфигураций:

```bash
# CrossPM: lock and recursive check packages
# Попытается сделать lock-файл для пакетов из dep.txt, при этом проверит его зависимости на использование одной версии пакетов
crosspm lock \
dependencies.txt dependencies.txt.lock \
--recursive \
--options cl="gcc-5.1",arch="x86_64",os="debian-8" \
--config=".\crosspm.lock.yaml"
(( $? )) && exit 1

# CrossPM: downloading packages
# Скачает только пакеты, которые указаны в dependencies.txt
crosspm download \
--config=".\crosspm.download.yaml" \
--lock-on-success \
--deps-path=".\dependencies.txt" \
--out-format="cmd" \
--output=".\klmn.cmd" \
--options cl="gcc-5.1",arch="x86_64",os="debian-8" \
(( $? )) && exit 1
```

<a class="mk-toclify" id="crosspm"></a>
## Хочу использовать кеш, но crosspm странно себя ведет - берет кеш пакета с другой версией?
На данный момент, если в пути до файла нет версии, например `repo/projectname/projectname/projectname.version.zip`
То архив разархивируется в папку `PROJECTNAME`.
В случае, когда выкачивается архив с новой версией `PROJECTNAME`, то он её не разархивирует, т.к. уже существует кэш с именем `PROJECTNAME`.

Решение - использовать кастомные пути до распакованных\запакованных файлов:

```yaml
cache:
storage:
packed: '{package}/{branch}/{version}/{compiler}/{arch}/{osname}/{package}.{version}.tar.gz'
unpacked: '{package}/{branch}/{version}/{compiler}/{arch}/{osname}'
```

<a class="mk-toclify" id="content"></a>
## Не хочу создавать dependencies-файл, хочу указать сразу в команде crosspm список пакетов
Для этого нужно запустить одну из команд:

```bash
# download - без указания --depslock-path
crosspm download --config config.yaml --dependencies-lock-content "boost 1.64.388 1.64-pm-icu" -o os=win,cl=vc140,arch=x86_64

# lock - БЕЗ указания файлов в начале. Создает по итогам файл dependencies.txt.lock
crosspm lock --config config.yaml --dependencies-content "boost 1.64.388 1.64-pm-icu" -o os=win,cl=vc140,arch=x86_64

# usedby - БЕЗ указания файлов в начале
crosspm usedby -c config.yaml --dependencies-content "packagename 1.2.* master"
```

<a class="mk-toclify" id="creds"></a>
## Как просто и безопасно передавать учётные данные в рамках crosspm. 

Для этого нужно задать переменные в конфигурационном файле. 

Подробнее можно [почитать тут](usage/USAGE-CREDS.md)


##
```Table of content auto generated: https://github.com/rasbt/markdown-toclify```