FROM python:3.11-alpine

# Устанавливаем зависимости системы (при необходимости)
RUN apk update && \
    apk add --no-cache \
        gcc \
        musl-dev \
        libffi-dev \
        openssl-dev \
        make \
        git \
        && rm -rf /var/cache/apk/*

# Устанавливаем рабочую директорию
WORKDIR /

# Сначала копируем только зависимости для использования кэша
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Команда для запуска приложения
CMD ["python", "main.py"]


RUN echo "source activate my_env" > ~/.bashrc

ENV PYTHONUNBUFFERED=1

ENV PATH /opt/conda/envs/my_env/bin:$PATH
