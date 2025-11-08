# test_config.py
import config # type: ignore

def main():
    print("REMOTIVE_API:", config.REMOTIVE_API)
    print("MIN_SIMILARITY:", config.MIN_SIMILARITY)
    print("ENABLE_TELEGRAM:", config.ENABLE_TELEGRAM)
    print("ENABLE_EMAIL:", config.ENABLE_EMAIL)
    print("SKILLS_JSON path:", config.SKILLS_JSON)

if __name__ == "__main__":
    main()
