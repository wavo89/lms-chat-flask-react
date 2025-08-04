#!/usr/bin/env python3
"""
Complete seeding script - runs all seed scripts in the correct order.
"""

import sys
import os

# Add both parent directory and db_scripts directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
db_scripts_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, db_scripts_dir)

from db_clear import clear_database
from db_create import create_database
from seed_admin import seed_admin
from seed_teacher import seed_teachers
from seed_student import seed_students
from seed_classes import seed_classes
from seed_assignments import seed_assignments
from seed_grades import seed_grades
from seed_attendance import seed_attendance

def seed_all():
    """Run all seeding scripts in the correct order."""
    print("🚀 Starting complete database seeding...")
    print("=" * 50)
    
    try:
        # Step 1: Clear existing data
        print("Step 1: Clearing existing database...")
        clear_database()
        print("✅ Database cleared\n")
        
        # Step 2: Create tables
        print("Step 2: Creating database tables...")
        create_database()
        print("✅ Tables created\n")
        
        # Step 3: Seed admin
        print("Step 3: Seeding admin account...")
        seed_admin()
        print("✅ Admin seeded\n")
        
        # Step 4: Seed teachers
        print("Step 4: Seeding teacher accounts...")
        seed_teachers()
        print("✅ Teachers seeded\n")
        
        # Step 5: Seed students
        print("Step 5: Seeding student accounts...")
        seed_students()
        print("✅ Students seeded\n")
        
        # Step 6: Seed classes
        print("Step 6: Seeding classes...")
        seed_classes()
        print("✅ Classes seeded\n")
        
        # Step 7: Seed assignments
        print("Step 7: Seeding assignments...")
        seed_assignments()
        print("✅ Assignments seeded\n")
        
        # Step 8: Seed grades
        print("Step 8: Seeding grades...")
        seed_grades()
        print("✅ Grades seeded\n")
        
        # Step 9: Seed attendance
        print("Step 9: Seeding attendance records...")
        seed_attendance()
        print("✅ Attendance seeded\n")
        
        print("=" * 50)
        print("🎉 Complete database seeding finished successfully!")
        print("\n💡 Login credentials:")
        print("   Admin: admin@test.com / Sample12")
        print("   Teacher: teacher1@test.com / Sample12") 
        print("   Student: student1@test.com / Sample12")
        print("\n📋 Database now contains:")
        print("   • 1 Admin account")
        print("   • 2 Teacher accounts") 
        print("   • 25 Student accounts")
        print("   • 2 Classes (Math & ELA) with ~80% student overlap")
        print("   • 6 Assignments (3 per class)")
        print("   • Realistic grades for all student-assignment combinations")
        print("   • 5 days of realistic attendance data")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        sys.exit(1)

if __name__ == '__main__':
    seed_all() 