#!/usr/bin/env python3
"""
Rhiz Skill Router CLI
Interactive command-line interface for skill recognition and routing.

Usage:
    python3 cli.py                    # Interactive mode
    python3 cli.py "check exchange"   # Single query mode
"""

import sys
from pathlib import Path
from engine import create_router

def print_banner():
    """Print CLI banner."""
    print("=" * 70)
    print(" " * 20 + "RHIZ SKILL ROUTER")
    print("=" * 70)

def print_skill_match(match, index=1, verbose=False):
    """Pretty print a skill match."""
    print(f"\n[{index}] {match['skill_name']}")
    print(f"    Confidence: {match['confidence']:.1%}")
    print(f"    Matched Pattern: \"{match['matched_pattern']}\"")
    print(f"    Similarity: {match['pattern_similarity']:.3f}")

    if verbose and 'skill_data' in match:
        skill = match['skill_data']['skill']
        print(f"    Domain: {skill.get('domain', 'unknown')}")
        print(f"    Version: {skill.get('version', 'unknown')}")

        if 'description' in skill:
            desc = skill['description'].strip().split('\n')[0]
            print(f"    Description: {desc[:60]}...")

def interactive_mode(router):
    """Run interactive query mode."""
    print("\nInteractive Mode - Enter queries to find matching skills")
    print("Commands:")
    print("  list          - Show all available skills")
    print("  primitives    - Show all available primitives")
    print("  info <skill>  - Show detailed info about a skill")
    print("  quit          - Exit")
    print()

    while True:
        try:
            query = input("skill> ").strip()

            if not query:
                continue

            if query.lower() in ['quit', 'exit', 'q']:
                print("\nFair winds! 🚢")
                break

            elif query.lower() == 'list':
                skills = router.list_skills()
                print(f"\nAvailable Skills ({len(skills)}):")
                for i, skill_name in enumerate(skills, 1):
                    info = router.get_skill_info(skill_name)
                    if info:
                        print(f"  {i}. {skill_name}")
                        print(f"     Domain: {info['domain']} | Tags: {', '.join(info['tags'][:3])}")
                continue

            elif query.lower() == 'primitives':
                primitives = router.list_primitives()
                print(f"\nAvailable Primitives ({len(primitives)}):")
                for i, prim_name in enumerate(primitives, 1):
                    print(f"  {i}. {prim_name}")
                continue

            elif query.lower().startswith('info '):
                skill_name = query[5:].strip()
                info = router.get_skill_info(skill_name)

                if info:
                    print(f"\nSkill: {info['name']}")
                    print(f"Version: {info['version']}")
                    print(f"Domain: {info['domain']}")
                    print(f"Tags: {', '.join(info['tags'])}")
                    print(f"\nDescription:")
                    print(f"  {info['description'].strip()}")
                else:
                    print(f"Skill '{skill_name}' not found")
                continue

            # Regular skill matching query
            print(f"\nSearching for skills matching: \"{query}\"")
            print("-" * 70)

            matches = router.recognize(query, top_k=3)

            if not matches:
                print("No skills matched. Try:")
                print("  - Using different keywords")
                print("  - Typing 'list' to see available skills")
            else:
                print(f"Found {len(matches)} matching skill(s):")
                for i, match in enumerate(matches, 1):
                    print_skill_match(match, index=i, verbose=True)

        except KeyboardInterrupt:
            print("\n\nFair winds! 🚢")
            break
        except Exception as e:
            print(f"Error: {e}")

def single_query_mode(router, query):
    """Run a single query and exit."""
    matches = router.recognize(query, top_k=3)

    if not matches:
        print(f"No skills matched query: \"{query}\"")
        print("\nAvailable skills:")
        for skill in router.list_skills():
            print(f"  - {skill}")
        return 1

    print(f"Matches for: \"{query}\"")
    print("-" * 70)

    for i, match in enumerate(matches, 1):
        print_skill_match(match, index=i, verbose=True)

    return 0

def main():
    """Main CLI entry point."""
    print_banner()

    # Initialize router
    print("\nInitializing skill router...")
    router = create_router()

    print(f"\nLoaded: {len(router.list_skills())} skills, {len(router.list_primitives())} primitives")

    # Check if query provided as argument
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
        return single_query_mode(router, query)
    else:
        interactive_mode(router)
        return 0

if __name__ == "__main__":
    sys.exit(main())
