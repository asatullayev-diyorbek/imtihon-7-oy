def write_to_env_file(key, value, env_file='.env'):
    try:
        # .env faylini ochamiz (yoki yaratamiz)
        with open(env_file, 'a') as file:  # 'a' bu faylga yozish rejimi (append)
            file.write(f'{key}={value}\n')  # key = value ko'rinishida yozamiz
        print(f"{key} muvaffaqiyatli qo'shildi.")
    except Exception as e:
        print(f"Xatolik yuz berdi: {e}")


if __name__ == '__main__':
    write_to_env_file("AUTH_USER_MODEL", 'user.User')