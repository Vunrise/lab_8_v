import multiprocessing
from multiprocessing import Pool, Event
import numpy as np
import time


# Функция для вычисления элемента результирующей матрицы
def calculate_element(args):
    i, j, A, B = args
    N = len(A[0])  # Количество столбцов в матрице A
    result = 0
    for k in range(N):
        result += A[i][k] * B[k][j]
    return (i, j, result)


# Функция для генерации случайной матрицы
def generate_matrix(size):
    return np.random.randint(1, 10, (size, size))


# Функция для перемножения матриц
def multiply_matrices(A, B, num_processes, stop_event):
    # Размеры матриц
    rows_A, cols_A = len(A), len(A[0])
    rows_B, cols_B = len(B), len(B[0])

    # Проверка на совместимость матриц
    if cols_A != rows_B:
        raise ValueError("Количество столбцов матрицы A должно совпадать с количеством строк матрицы B!")

    # Подготовка аргументов для пула процессов
    tasks = [(i, j, A, B) for i in range(rows_A) for j in range(cols_B)]

    # Пул процессов
    with Pool(num_processes) as pool:
        results = []
        for result in pool.imap(calculate_element, tasks):
            if stop_event.is_set():  # Проверка на остановку
                print("Процесс перемножения остановлен.")
                return None
            results.append(result)

    # Создаем результирующую матрицу
    C = [[0] * cols_B for _ in range(rows_A)]
    for i, j, value in results:
        C[i][j] = value

    return C


# Основная программа
if __name__ == "__main__":
    # Размер матрицы
    size = int(input("Введите размер квадратной матрицы: "))

    # Генерация случайных матриц
    print("Генерация случайных матриц...")
    A = generate_matrix(size)
    B = generate_matrix(size)

    print("Матрица A:")
    print(A)
    print("Матрица B:")
    print(B)

    # Определение количества процессов
    num_processes = multiprocessing.cpu_count()
    print(f"Используемое количество процессов: {num_processes}")

    # Создание события для остановки
    stop_event = Event()

    # Запуск перемножения в асинхронном режиме
    try:
        print("Начало перемножения матриц...")
        result_process = multiprocessing.Process(
            target=lambda: print(
                "Результирующая матрица:\n", 
                np.array(multiply_matrices(A, B, num_processes, stop_event))
            )
        )
        result_process.start()

        # Имитируем работу с возможностью остановки
        time.sleep(2)  # Ожидаем 2 секунды перед возможной остановкой
        if input("Введите 'stop' для остановки процесса: ").lower() == "stop":
            stop_event.set()
            result_process.terminate()

        result_process.join()
    except KeyboardInterrupt:
        print("\nОстановка программы.")
        stop_event.set()
        result_process.terminate()
