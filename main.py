# Verify-First Agent - النسخة المخففة
def verify(claim, evidence):
    if not evidence:
        return "مرفوض - مافي دليل"
    if evidence in claim:
        return "مقبول - تم التحقق"
    return "يحتاج مراجعة"

def main():
    print("=== Verify-First Agent ===")
    claim = input("الادعاء: ")
    evidence = input("الدليل: ")
    print(verify(claim, evidence))

if __name__ == "__main__":
    main()
