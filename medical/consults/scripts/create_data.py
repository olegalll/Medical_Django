from faker import Faker
from consults.models import User, Clinic

fake = Faker()


def create_fake_data():
    # Создание клиник
    for _ in range(5):
        clinic = Clinic.objects.create(
            name=fake.company(),
            address=fake.address(),
            physical_address=fake.address()
        )
        print(f"Clinic created: {clinic.name}")

    # Создание докторов и пациентов
    for _ in range(20):
        user = User.objects.create_user(
            username=fake.user_name(),
            email=fake.email(),
            password="password",
            role="doctor",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            surname=fake.last_name(),
        )
        print(f"Doctor created: {user.username}")

    for _ in range(20):
        user = User.objects.create_user(
            username=fake.user_name(),
            email=fake.email(),
            password="password",
            role="patient",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone=fake.phone_number(),
        )
        print(f"Patient created: {user.username}")

    print("All data generation complete.")
