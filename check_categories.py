#!/usr/bin/env python3
"""
Script to check current topic categories
"""

from counseling_database import COUNSELING_TOPICS

def check_categories():
    print("Current topic categories:")
    for key, data in COUNSELING_TOPICS.items():
        print(f"• {data['icon']} {data['name']}")

if __name__ == "__main__":
    check_categories()