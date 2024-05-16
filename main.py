import counter_service
import lotus
import baac
import mpay
import true

def run_all():
    try:
        print("Running counter_service.py")
        counter_service.main()
    except Exception as e:
        print(f"Error running counter_service.py: {e}")

    try:
        print("Running mpay.py")
        mpay.main()
    except Exception as e:
        print(f"Error running mpay.py: {e}")

    try:
        print("Running baac.py")
        baac.main()
    except Exception as e:
        print(f"Error running baac.py: {e}")

    try:
        print("Running true.py")
        true.main()
    except Exception as e:
        print(f"Error running mpay.py: {e}")

    try:
        print("Running lotus.py")
        lotus.main()
    except Exception as e:
        print(f"Error running lotus.py: {e}")

    # try:
    #     print("Running lotus.py")
    #     lotus-tims.main()
    # except Exception as e:
    #     print(f"Error running lotus-tims.py: {e}")

if __name__ == "__main__":
    run_all()
