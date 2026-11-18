from agent import solve

def handler(question: str):
    return solve(question)

# للتجربة محليا
if __name__ == "__main__":
    print(solve("Calculate 3-phase power for 400V, 100A"))
    print(solve("Torque for power 50000W at 1500 RPM"))
    print(solve("Voltage drop for current 150A distance 80m cable 50mm2"))
