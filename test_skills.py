# test_skills.py
import json
import config

def main():
    with open(config.SKILLS_JSON, "r", encoding="utf-8") as f:
        skills = json.load(f)
    
    print("✅ Technical skills loaded:", len(skills["technical_skills"]))
    print("✅ Soft skills loaded:", len(skills["soft_skills"]))
    print("✅ Tools loaded:", len(skills["tools"]))
    print("✅ Roles of interest loaded:", len(skills["roles_of_interest"]))

if __name__ == "__main__":
    main()
