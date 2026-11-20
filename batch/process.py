"""
MiddleDock Batch Processor — answer a list of employee questions from a CSV.

Usage: python process.py --input questions.csv --output answers.csv

Input CSV format:
  question
  "How many PTO days do I get?"
  "What's the expense limit for flights?"

Output CSV adds an 'answer' column.
"""

import sys
sys.path.append("..")

import csv
import argparse
import time
from agent.rag import MiddleDockAgent


def process_batch(input_file: str, output_file: str):
    agent = MiddleDockAgent()

    with open(input_file, "r") as f:
        reader = csv.DictReader(f)
        questions = list(reader)

    print(f"Processing {len(questions)} questions...")

    results = []
    for i, row in enumerate(questions):
        question = row["question"]
        print(f"[{i+1}/{len(questions)}] {question[:60]}...")

        start = time.time()
        answer = agent.ask(question)
        elapsed = time.time() - start

        results.append({
            "question": question,
            "answer": answer,
            "latency_seconds": round(elapsed, 2),
        })

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["question", "answer", "latency_seconds"])
        writer.writeheader()
        writer.writerows(results)

    total_latency = sum(r["latency_seconds"] for r in results)
    print(f"\nDone. {len(results)} answers written to {output_file}")
    print(f"Total time: {total_latency:.1f}s, Avg: {total_latency/len(results):.1f}s per question")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="questions.csv")
    parser.add_argument("--output", default="answers.csv")
    args = parser.parse_args()
    process_batch(args.input, args.output)
