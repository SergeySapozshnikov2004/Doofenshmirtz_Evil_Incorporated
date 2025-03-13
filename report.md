@startuml
title "Сценарий 1. Нормальная работа системы Бэтмобиля с участием Бэтмена"

participant "Альфред" as alfred
participant "Бэтмен" as batman
participant "Система планирования в авто" as planning
participant "Навигационная система" as navigation
participant "Система управления движением" as motion_control
participant "Система безопасности" as security
participant "Система связи" as communication
participant "Логирование" as logging
participant "Автопилот Бэтмобиля" as autopilot
participant "Система диагностики" as diagnostics
participant "Система жизнеобеспечения" as life_support
participant "Система мониторинга" as monitoring
participant "Система отчетности" as reporting
participant "Система энергопотребления" as energy_management
participant "Система управления критическими ситуациями" as crit_control
participant "Система анализа данных" as data_analysis

autonumber

alfred -> planning: Запрос на планирование миссии
planning -> navigation: Получение текущих координат
navigation -> planning: Текущие координаты
planning -> navigation: Расчет маршрута до цели
navigation -> planning: Маршрут рассчитан
planning -> alfred: Маршрут готов
alfred -> batman: Передача данных о миссии и маршруте
batman -> planning: Подтверждение маршрута
planning -> batman: Маршрут подтвержден

batman -> motion_control: Запуск движения по маршруту
motion_control -> autopilot: Активация автопилота
autopilot -> motion_control: Автопилот активирован
motion_control -> navigation: Следование по маршруту
navigation -> motion_control: Корректировка движения
motion_control -> security: Проверка безопасности маршрута
security -> motion_control: Маршрут безопасен

motion_control -> life_support: Проверка состояния систем жизнеобеспечения
life_support -> motion_control: Все системы в норме

motion_control -> energy_management: Проверка уровня энергии
energy_management -> motion_control: Уровень энергии в норме

motion_control -> crit_control: Проверка критической ситуации
crit_control -> motion_control: Система управления критическимми ситуацими готово к использованию

loop [Движение по маршруту]
    motion_control -> navigation: Обновление данных о местоположении
    navigation -> motion_control: Данные обновлены
    motion_control -> security: Постоянный мониторинг безопасности
    security -> motion_control: Угроз не обнаружено
    motion_control -> diagnostics: Проверка состояния систем
    diagnostics -> motion_control: Все системы в норме
    motion_control -> monitoring: Мониторинг окружающей среды
    monitoring -> motion_control: Данные мониторинга
    motion_control -> data_analysis: Анализ данных
    data_analysis -> motion_control: Анализ завершен
    motion_control -> batman: Отчет о текущем состоянии
    batman -> motion_control: Команды на корректировку (при необходимости)
end

motion_control -> batman: Прибытие в пункт назначения
batman -> communication: Отчет о завершении миссии
communication -> reporting: Формирование отчета
reporting -> communication: Отчет готов
communication -> logging: Логирование завершения миссии
logging -> communication: Логирование завершено
communication -> alfred: Отчет отправлен
alfred -> batman: Подтверждение завершения миссии
@enduml
