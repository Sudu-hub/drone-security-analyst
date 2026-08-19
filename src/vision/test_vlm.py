from src.vision.vlm_analyzer import VLMAnalyzer


def main():

    analyzer = VLMAnalyzer()

    result = analyzer.analyze_description(
        description=(
            "A blue Ford F150 is entering "
            "through the main gate."
        ),
        timestamp="00:00",
        location="main_gate"
    )

    print("\nVLM OUTPUT")
    print("=" * 50)

    print(result)

    print("\nVALIDATION")
    print("=" * 50)

    print(
        analyzer.validate_result(result)
    )


if __name__ == "__main__":
    main()