import argparse
from checker import load_endpoints, check_endpoint, save_results
from reporter import generate_report


def parse_arguments():
    parser = argparse.ArgumentParser(description="API Health Checker")
    parser.add_argument("--file", default="endpoints.json", help="Path to endpoints file")
    parser.add_argument("--output", default="history/results.json", help="Path to save results")
    parser.add_argument("--report", default="reports/report.html", help="Path to save HTML report")
    parser.add_argument("--check", action="store_true", help="Run health check")
    parser.add_argument("--generate-report", action="store_true", help="Generate HTML report")
    return parser.parse_args()


def main():
    args = parse_arguments()
    print(f"check={args.check}, report={args.generate_report}")

    if args.check:
        endpoints = load_endpoints(args.file)
        results = []
        for ep in endpoints:
            result = check_endpoint(ep)
            results.append(result)
            print(f"{result['name']}: {result['status']}")
        save_results(results, args.output)

    if args.generate_report:
        generate_report(args.output, args.report)

    if not args.check and not args.generate_report:
        print("Set flag: --check, --generate-report, or both")


if __name__ == "__main__":
    main()

