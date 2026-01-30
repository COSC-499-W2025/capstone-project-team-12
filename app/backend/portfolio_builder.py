from typing import Dict, Any, Optional, List
import uuid
from cli_interface import CLI

from database_manager import DatabaseManager
from portfolio_data_processor import PortfolioDataProcessor


class PortfolioBuilder:
    """
    Main class for coordinating portfolio generation from analysis results.
    Handles portfolio building, database integration, and display.
    
    Portfolios showcase detailed project deep-dives and demonstrate learning
    progression through skill evolution and growth metrics.

    DATABASE IMPLEMENTATION PLAN:
    -----------------------------
    Future database schema will have a 'portfolios' table with columns:
    - portfolio_id (PK, UUID)
    - result_id (FK to results table, UUID)
    - projects_detail (JSON) - Top 3 projects with comprehensive data
    - skill_timeline (JSON) - Complete skill evolution across all projects
    - growth_metrics (JSON) - Comparative metrics showing progression
    - full_portfolio (JSON) - Complete portfolio object for easy retrieval
    
    Each column stores an individual component, plus full_portfolio stores
    the entire portfolio dictionary. This allows:
    1. Querying/updating individual sections
    2. Fast retrieval of complete portfolio
    3. Frontend can request specific sections or full portfolio
    
    Example future database methods:
    - database_manager.save_portfolio(portfolio) -> stores all columns
    - database_manager.get_portfolio_by_id(portfolio_id) -> returns full portfolio
    - database_manager.update_portfolio_section(portfolio_id, section_name, data)
    """

    def create_portfolio_from_result_id(self, database_manager: DatabaseManager, cli: CLI, result_id: str) -> Optional[Dict[str, Any]]:
        """
        Builds the portfolio from a stored result by fetching from the database.
        
        Args:
            database_manager: DatabaseManager instance
            cli: CLI interface for user feedback
            result_id: UUID of the result to generate portfolio from
        
        Returns:
            Portfolio dictionary or None if generation fails
        """
        try:
            cli.print_header(f"Retrieving result {result_id} for portfolio generation...")
            
            # Fetch the result data from the database
            result_data = database_manager.get_analysis_data(result_id)
            
            if not result_data:
                cli.print_status("Result not found in database.", "error")
                return None
            
            cli.print_status("Generating portfolio...", "info")
            
            # Build the actual portfolio with all sections
            portfolio = self._build_portfolio(result_data, result_id=result_id)
            
            # Ensure portfolio has content
            has_content = any([
                portfolio.get('projects_detail'),
                portfolio.get('skill_timeline'),
                portfolio.get('growth_metrics')
            ])
            
            if not has_content:
                cli.print_status("Generated portfolio is empty. Cannot save or display.", "error")
                return None
            
            cli.print_status("Portfolio generated successfully!", "success")
            
            return portfolio
        
        except Exception as e:
            cli.print_status(f"Error creating portfolio: {e}", "error")
            return None

    def _build_portfolio(self, result_data: Dict[str, Any], result_id: str) -> Dict[str, Any]:
        """
        Internal method to build the portfolio dictionary from result data.
        
        Args:
            result_data: Dictionary containing all analysis results
            result_id: UUID of the result
        
        Returns:
            Portfolio dictionary with sections: portfolio_id, result_id,
            projects_detail, skill_timeline, growth_metrics.
            This structure maps directly to the planned database schema.
        """
        try:
            processor = PortfolioDataProcessor(result_data)
            
            # Extract detailed projects (top 3, chronologically sorted)
            projects_detail = processor.extract_detailed_projects(top_n=3)
            
            # Extract complete skill timeline (uses all metadata)
            skill_timeline = processor.extract_skill_timeline(projects_detail)
            
            # Calculate growth metrics (comparing earliest vs latest project)
            growth_metrics = processor.calculate_growth_metrics(projects_detail)
            
            # Construct portfolio dictionary
            portfolio = {
                "portfolio_id": str(uuid.uuid4()),
                "result_id": result_id,
                "projects_detail": projects_detail,
                "skill_timeline": skill_timeline,
                "growth_metrics": growth_metrics
            }
            
            return portfolio
        
        except Exception as e:
            print(f"Error building portfolio: {e}")
            return {}

    def display_portfolio(self, portfolio: Dict[str, Any], cli=None) -> None:
        """
        Display portfolio in CLI with comprehensive formatting.
        Shows project deep-dives, skill evolution, and growth metrics.
        
        Args:
            portfolio: Portfolio dictionary
            cli: CLI interface for formatted display
        """
        try:
            cli.print_header("DEVELOPER PORTFOLIO")
            
            # Display portfolio metadata
            print(f"Portfolio ID: {portfolio.get('portfolio_id', 'Unknown')}")
            print(f"Result ID: {portfolio.get('result_id', 'Unknown')}")
            print("")
            
            # Display growth metrics first (demonstrates evolution)
            growth_metrics = portfolio.get('growth_metrics', {})
            if growth_metrics.get('has_comparison'):
                self._display_growth_metrics(growth_metrics)
            
            # Display detailed projects section
            projects = portfolio.get('projects_detail', [])
            if projects:
                self._display_detailed_projects(projects)
            
            # Display skill timeline section
            skill_timeline = portfolio.get('skill_timeline', {})
            if skill_timeline:
                self._display_skill_timeline(skill_timeline)
            
            print("=" * 80)
            
        except Exception as e:
            if cli:
                cli.print_status(f"Error displaying portfolio: {e}", "error")
            else:
                print(f"Error displaying portfolio: {e}")

    def _display_growth_metrics(self, growth_metrics: Dict[str, Any]) -> None:
        """
        Display comprehensive growth comparison metrics showing learning progression.
        
        Args:
            growth_metrics: Growth metrics dictionary with nested structure
        """
        print("LEARNING PROGRESSION & EVOLUTION")
        print("=" * 80)
        print(f"Comparing: {growth_metrics.get('earliest_project', 'Unknown')} → {growth_metrics.get('latest_project', 'Unknown')}")
        print("")
        
        # Code metrics
        code_metrics = growth_metrics.get('code_metrics', {})
        print("Code Volume Growth:")
        print(f"   • Commit Activity: {self._format_growth(code_metrics.get('commit_growth', 0))}")
        print(f"   • Project Scope (files): {self._format_growth(code_metrics.get('file_growth', 0))}")
        print(f"   • Total Code Volume (net lines): {self._format_growth(code_metrics.get('lines_growth', 0))}")
        print(f"   • Your Code Contribution: {self._format_growth(code_metrics.get('user_lines_growth', 0))}")
        print("")
        
        # Technology metrics
        tech_metrics = growth_metrics.get('technology_metrics', {})
        framework_growth = tech_metrics.get('framework_growth', 0)
        earliest_fw = tech_metrics.get('earliest_frameworks', 0)
        latest_fw = tech_metrics.get('latest_frameworks', 0)
        print("Technology Stack Evolution:")
        print(f"   • Frameworks/Libraries: {self._format_growth(framework_growth)}")
        print(f"     ({earliest_fw} frameworks → {latest_fw} frameworks)")
        print("")
        
        # Testing evolution
        testing_evolution = growth_metrics.get('testing_evolution', {})
        earliest_tests = testing_evolution.get('earliest_has_tests', False)
        latest_tests = testing_evolution.get('latest_has_tests', False)
        coverage_change = testing_evolution.get('coverage_improvement', 0)
        
        print("Testing Practice Evolution:")
        if not earliest_tests and latest_tests:
            print(f"   Adopted testing practices! (0% → {coverage_change:.1f}% test coverage)")
        elif earliest_tests and latest_tests:
            if coverage_change > 0:
                print(f"   Improved test coverage by {coverage_change:.1f}%")
            elif coverage_change < 0:
                print(f"   Test coverage decreased by {abs(coverage_change):.1f}%")
            else:
                print(f"   Maintained consistent testing practices")
        elif earliest_tests and not latest_tests:
            print(f"   Testing practices not present in latest project")
        else:
            print(f"   • No testing detected in either project")
        print("")
        
        # Collaboration evolution
        collab_evolution = growth_metrics.get('collaboration_evolution', {})
        earliest_solo = collab_evolution.get('earliest_solo', True)
        latest_solo = collab_evolution.get('latest_solo', True)
        earliest_team = collab_evolution.get('earliest_team_size', 1)
        latest_team = collab_evolution.get('latest_team_size', 1)
        earliest_level = collab_evolution.get('earliest_level', 'Unknown')
        latest_level = collab_evolution.get('latest_level', 'Unknown')
        
        print("Collaboration & Teamwork Evolution:")
        if earliest_solo and not latest_solo:
            print(f"   Transitioned from solo work to team collaboration")
            print(f"     (Solo → Team of {latest_team})")
            print(f"     Role: {latest_level}")
        elif not earliest_solo and not latest_solo:
            if latest_team > earliest_team:
                print(f"   Working with larger teams ({earliest_team} → {latest_team} contributors)")
            elif latest_team < earliest_team:
                print(f"   Working with smaller teams ({earliest_team} → {latest_team} contributors)")
            else:
                print(f"   Consistent team size ({latest_team} contributors)")
            print(f"     Contribution level: {earliest_level} → {latest_level}")
        elif not earliest_solo and latest_solo:
            print(f"   Transitioned from team collaboration to solo work")
            print(f"     (Team of {earliest_team} → Solo)")
        else:
            print(f"   • Consistent solo development approach")
        print("")
        
        # Role evolution
        role_evolution = growth_metrics.get('role_evolution', {})
        earliest_role = role_evolution.get('earliest_role', 'Unknown')
        latest_role = role_evolution.get('latest_role', 'Unknown')
        role_changed = role_evolution.get('role_changed', False)
        
        print("Role & Contribution Style Evolution:")
        if role_changed:
            print(f"   {earliest_role} → {latest_role}")
            print(f"   Development approach evolved over time")
        else:
            print(f"   Consistent role: {latest_role}")
        print("")

    def _format_growth(self, percentage: float) -> str:
        """
        Format growth percentage with appropriate sign and color indication.
        
        Args:
            percentage: Growth percentage value
            
        Returns:
            Formatted string with sign
        """
        if percentage > 0:
            return f"+{percentage}%"
        elif percentage < 0:
            return f"{percentage}%"
        else:
            return "No change"

    def _display_detailed_projects(self, projects: List[Dict[str, Any]]) -> None:
        """
        Display detailed project showcases with comprehensive metrics.
        
        Args:
            projects: List of detailed project dictionaries
        """
        print("PROJECT DEEP DIVES")
        print("=" * 80)
        
        for idx, project in enumerate(projects, 1):
            print(f"\n{'─' * 80}")
            print(f"PROJECT {idx}: {project.get('name', 'Unknown Project')}")
            print(f"{'─' * 80}")
            print(f"Timeline: {project.get('date_range', 'Dates unavailable')}")
            duration = project.get('duration_days', 0)
            if duration > 0:
                print(f"Duration: {duration} days")
            print("")
            
            # Display user role
            user_role = project.get('user_role', {})
            if user_role.get('role'):
                print(f"Role: {user_role.get('role')}")
                print(f"   {user_role.get('blurb', '')}")
                print("")
            
            # Display contribution analysis
            contribution = project.get('contribution', {})
            print("Contribution Analysis:")
            print(f"   Level: {contribution.get('level', 'Unknown')}")
            
            if contribution.get('is_collaborative'):
                team_size = contribution.get('team_size', 1)
                rank = contribution.get('rank')
                percentile = contribution.get('percentile')
                share = contribution.get('contribution_share', 0)
                
                print(f"   Team Size: {team_size} contributors")
                if rank:
                    print(f"   Rank: #{rank} out of {team_size}")
                if percentile is not None:
                    print(f"   Percentile: {percentile}th")
                print(f"   Contribution Share: {share:.1f}% of total commits")
            else:
                print(f"   Solo project")
            print("")
            
            # Display statistics
            stats = project.get('statistics', {})
            print("Project Statistics:")
            print(f"   Total Project:")
            print(f"      • Commits: {stats.get('commits', 0)}")
            print(f"      • Files: {stats.get('files', 0)}")
            print(f"      • Lines Added: +{stats.get('additions', 0):,}")
            print(f"      • Lines Deleted: -{stats.get('deletions', 0):,}")
            print(f"      • Net Lines: {stats.get('net_lines', 0):,}")
            
            # Show user-specific stats
            user_commits = stats.get('user_commits', 0)
            user_additions = stats.get('user_lines_added', 0)
            user_deletions = stats.get('user_lines_deleted', 0)
            user_net = stats.get('user_net_lines', 0)
            user_files = stats.get('user_files_modified', 0)
            
            print(f"   Your Contribution:")
            print(f"      • Commits: {user_commits}")
            print(f"      • Lines Added: +{user_additions:,}")
            print(f"      • Lines Deleted: -{user_deletions:,}")
            print(f"      • Net Lines: {user_net:,}")
            print(f"      • Files Modified: {user_files}")
            print("")
            
            # Display testing insights
            testing = project.get('testing', {})
            if testing.get('has_tests'):
                print("Testing & Quality:")
                test_files = testing.get('test_files', 0)
                code_files = testing.get('code_files', 0)
                coverage_files = testing.get('coverage_by_files', 0)
                coverage_lines = testing.get('coverage_by_lines', 0)
                
                print(f"   • Test Files: {test_files} ({coverage_files:.1f}% of modified files)")
                print(f"   • Code Files: {code_files}")
                print(f"   • Test Coverage by Lines: {coverage_lines:.1f}%")
                print("")
            
            # Display technologies
            frameworks = project.get('frameworks', [])
            if frameworks:
                print("Technologies & Frameworks:")
                # Display top frameworks with frequency
                for framework in frameworks[:10]:  # Show top 10
                    freq = framework.get('frequency', 0)
                    name = framework.get('name', 'Unknown')
                    print(f"   • {name} (used {freq}x)")
                
                if len(frameworks) > 10:
                    print(f"   ... and {len(frameworks) - 10} more")
                print("")
        
        print("")

    def _display_skill_timeline(self, skill_timeline: Dict[str, Any]) -> None:
        """
        Display comprehensive skill evolution timeline with separation between
        high-level skills and technical frameworks.
        
        Args:
            skill_timeline: Skill timeline dictionary
        """
        print("SKILL EVOLUTION & TECHNICAL GROWTH")
        print("=" * 80)
        
        high_level_skills = skill_timeline.get('high_level_skills', [])
        framework_timeline = skill_timeline.get('framework_timeline', {})
        language_progression = skill_timeline.get('language_progression', [])
        
        # Display high-level skills overview
        print(f"Core Competencies ({len(high_level_skills)} skills):")
        if high_level_skills:
            skills_str = ", ".join(high_level_skills)
            # Wrap text at reasonable width
            import textwrap
            wrapped = textwrap.fill(skills_str, width=76, initial_indent="   ", subsequent_indent="   ")
            print(wrapped)
            print("")
        
        # Display framework/library progression across projects
        if framework_timeline:
            print("Technical Framework Evolution (Chronological):")
            for project_name, proj_data in framework_timeline.items():
                date_range = proj_data.get('date_range', 'Unknown')
                frameworks = proj_data.get('frameworks', [])
                total_fw = proj_data.get('total_frameworks', 0)
                
                print(f"\n   {project_name} ({date_range})")
                if frameworks:
                    frameworks_str = ", ".join(frameworks)
                    wrapped = textwrap.fill(frameworks_str, width=73, initial_indent="      ", subsequent_indent="      ")
                    print(wrapped)
                    if total_fw > len(frameworks):
                        print(f"      ... and {total_fw - len(frameworks)} more")
            print("")
        
        # Display language progression
        if language_progression:
            print("Programming Language Proficiency:")
            for lang in language_progression:
                name = lang.get('name', 'Unknown')
                file_count = lang.get('file_count', 0)
                percentage = lang.get('percentage', 0)
                
                # Create visual bar (simple text-based)
                bar_length = int(percentage / 5)  # Scale to reasonable length
                bar = "█" * bar_length
                
                print(f"   • {name:12} {bar} {percentage:.1f}% ({file_count} files)")
            print("")