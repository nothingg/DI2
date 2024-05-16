import counter_service
import lotus
import baac
import lotus_tims
import mpay
import true

def run_all():
    input_date = '2024-05-15'
    try:
        print("Running counter_service.py")
        counter_service.main(input_date)
    except Exception as e:
        print(f"Error running counter_service.py: {e}")

    try:
        print("Running mpay.py")
        mpay.main(input_date)
    except Exception as e:
        print(f"Error running mpay.py: {e}")

    try:
        print("Running baac.py")
        baac.main(input_date)
    except Exception as e:
        print(f"Error running baac.py: {e}")

    try:
        print("Running true.py")
        true.main(input_date)
    except Exception as e:
        print(f"Error running mpay.py: {e}")

    try:
        print("Running lotus.py")
        lotus.main(input_date)
    except Exception as e:
        print(f"Error running lotus.py: {e}")

    try:
        print("Running lotus_tims.py")
        lotus_tims.main(input_date)
    except Exception as e:
        print(f"Error running lotus_tims.py: {e}")

if __name__ == "__main__":
    run_all()
