# Змейка

## Описание

Обычная змейка, которая увеличивается при поедании еды. Есть 3 режима запуска:
- run_manual - управление змейкой осуществляется с клавиатуры
- run_generation - змейка управляется генетическим алгоритмом с помощью библиотеки `neat-python`
- run_hamilton - змейка управляется алгоритмом поиска гамильтонова цикла

Режим запуска можно изменить в файле `main.py`.

## Управление

- `Стрелка вверх` - движение вверх
- `Стрелка вниз` - движение вниз
- `Стрелка влево` - движение влево
- `Стрелка вправо` - движение вправо
- `Пробел` - ускорение змейки для режима `run_hamilton`

## Установка

1\. Установите зависимости:
```bash
pip install poetry
poetry install
```

2\. Запустите игру:
```bash
poetry run python -m main
```
