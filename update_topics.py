#!/usr/bin/env python3
"""
Script to update old topic categories to new ones and fix counselor specializations
"""

import sqlite3
import json

def update_topics():
    # Connect to database
    conn = sqlite3.connect('hu_counseling.db')
    cursor = conn.cursor()
    
    # Mapping of old topics to new topics
    topic_mapping = {
        'family': 'relationships_social',
        'financial': 'academic_career',
        'ministry': 'life_skills_growth',
        'grief': 'mental_emotional',
        'crisis': 'crisis_substance',
        'relationships': 'relationships_social',
        'academic': 'academic_career',
        'doubt': 'mental_emotional',
        'general': 'other'
    }
    
    # Update pending sessions with old topics
    updated_count = 0
    for old_topic, new_topic in topic_mapping.items():
        cursor.execute(
            'UPDATE counseling_sessions SET topic = ? WHERE topic = ? AND status = "requested"',
            (new_topic, old_topic)
        )
        count = cursor.rowcount
        if count > 0:
            print(f"Updated {count} sessions from '{old_topic}' to '{new_topic}'")
            updated_count += count
    
    print(f"Total sessions updated: {updated_count}")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("Topic updates completed successfully!")

if __name__ == "__main__":
    update_topics()