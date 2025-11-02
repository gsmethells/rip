# Rules

**IMPORTANT**: This file contains rules that must be followed concerning coding standards and workflows for the projects in this repo.

## General Code Standards

### Headers
- Include a copyright header in files with at least one line of code
  - use the last four lines from the COPYRIGHT file
  - use a language-specific comment style

### Spaces and Wrapping
- Use two spaces instead of tabs
- Wrap lines at 120 characters
- Do NOT leave space characters at the end of a line

### Blank Lines

**MANDATORY**: Always follow these blank line rules

#### Code Block Definitions for Blank Line Rules
- **Assignment block**:
  - One or more consecutive assignment statements (including comprehensions and lambdas assigned to a variable)
- **Call block**:
  - One or more consecutive statements containing:
    - function/method calls
    - composite function/method calls (e.g., "foo(bar())")
    - chained method calls (e.g., "alpha.foo().bar()")
    - del, assert, pass, raise, yield, or return statements
- **Import block**: One or more consecutive import statements
- **Control block**:
  - Complete control structures suc as if/elif/else, for/else, while/else, try/except/else/finally, with/as
  - Any control structure is "complete" once the last statement within the body of the control structure is reached
     - For control structures that use optional clauses (elif, else, finally, etc.) this is the last statement within the body of that optional clause
- **Definition block**:
  - A single complete def or class structure (including docstring), from (single or stacked) decorators (if any) through the last statement in its body
    - Any definition structure is "complete" once the last statement within the body of the definition structure is reached
- **Declaration block**:
  - One or more consecutive global or nonlocal statements
- **Comment block**
  - One or more consecutive comment lines

#### Blank Line Rules
- The primary rule: place a blank line after a **block** when the next **block** is a different type of **block**
- The only exceptions to the primary rule:
  - Consecutive **Control blocks** or **Definition blocks** within the same scope must be separated by a blank line
  - No blank line is required after a **Comment block**, but if one is present then leave it as-is
  - No blank line at the start or end of any scope (file or body)
- For nested control structures, apply blank line rules at each level independently

#### Blank Line Rule Caveats
- A multiline statement (e.g., function call or assignment) counts as one statement
- Classification precedence between a **Call block** or an **Assignment block** favors an **Assignment block**

### Naming Conventions
- Use camelCase for variable, function, and method names
- Use PascalCase for class names
- Use UPPER_CASE for constants and environment variables
- Use all lower-case filenames (with no underscores) composed of (at most) a three word description of the file's purpose

### Control Flow

**MANDATORY**: Always follow these rules regarding control flow.

- Use exceptions instead return statements for control flow between caller/callee when there are errors
- Use only one return statement in a function/method unless:
  - the extra return statement is part of a guard clause near the beginning of the function/method
  - the extra return statement is part of an inner function definition
- Always include an "else" clause when an if-statement has an "else if" clause

### Documentation
- Document complex business logic
- Include XXX comments for non-obvious logic or important implementation notes

## Project Structure
- Keep code modular aiming to maintain a Separation of Concerns
- Keep functions and methods short and focused
- Organize code into logical packages based upon the purpose of the class/module
- Follow existing directory/package structure patterns
- Use environment variables for configuration
- Keep configuration separate from business logic

### Error Handling
- Use custom exception classes for domain-specific errors
- Include meaningful error messages
- Use retry mechanisms for network operations
- Log errors appropriately with context

### Security
- Use secure defaults for all configurations
- Validate all input data
- Follow security best practices

### Performance
- Use appropriate data structures
- Use async/await where appropriate
- Consider memory usage for I/O operations
- Achieve correctness first and optimize later: this prevents premature optimization

### Code Quality & Linting
- **Run `ruff check` and `ruff format` to ensure code quality**
- Follow ruff configuration settings in `pyproject.toml` in the git repo root
- All code must pass ruff checks so fix all ruff violations
- Common ruff violations to avoid:
  - E722: Use specific exception types, not bare `except:`
  - F401: Remove unused imports
  - E501: Line too long (follow 120 character limit)

### Testing

#### General Standards
- **MANDATORY**: When fixing a bug, **always** add regression tests to the existing unit test suite
- Prefer short, to-the-point tests that test situations corresponding to a single use case
- Do not call private methods directly inside unit tests
- Never mock methods of the class under test
- Use mocks only when necessary, for example:
  - when using a third-party interface (e.g, an API call) **always** use a mock
  - when natural set up would be too difficult (e.g., a race condition)

#### Unit Tests
- Add tests to the appropriate existing test file (e.g., `test/parser/test_featureextractor.py`)
- Include clear documentation in test names and docstrings explaining what bug the test prevents
- Test both success and failure scenarios for the function/method
- Aim for complete test coverage of the function/method
- Do not let unit tests become integration tests: focus on testing the function/method at-hand

## Python Coding Standards

### Syntax
- Use Python 3.11 syntax and features
- Do not use type hints from the typing module unless needed for a dataclass

### Formatting
- Follow the Black project's style guide except where it conflicts with rules in this file

### Project Structure
- Use `__init__.py` files for package initialization
- Use pyproject.toml for Python dependency management instead of requirements.txt
- Follow PEP 621 standards for project metadata and dependency specification

### Quotes
- Use single quotes for strings
- Use triple double quotes for docstrings

### Imports
- Use explicit imports and not wildcard imports
- Use absolute imports and not relative imports
- Keep imports at the top of a function, method, or file

### Docstring
- Include reST style docstrings for all functions and classes which can use `type` and `rtype` annotations

### Unit Tests
- **Test file naming**: Use `test_` prefix + exact source filename (e.g., `foo.py` → `test_foo.py`)
- Each source file has exactly ONE unit test file
- **Unit tests**: Place in `test/` with structure mirroring source (e.g., `core/foo.py` → `test/core/test_foo.py`)
- **Integration tests**: Place in `test/integration/` with descriptive names (e.g., `test/integration/test_commands.py`)
- Write unit tests using pytest and mocker
- Always run tests using `pytest` (not `python -m pytest`)
- Override the rule for function names in the test suite for functions that are a test function:
  - use a prefix `test_` followed by a suffix in camelCase describing the purpose of the test
    - For example: `test_checkForInvalidCeId` or `test_auditFeatueFileAssoctionNoIssues`

## Implementation Consistency

When making any design change or decision that affects multiple parts of the codebase:

1. Trace all implications - Identify every file, function, comment, error message, and documentation that needs updating
2. Update everything consistently - Don't leave stale comments, outdated error messages, or mismatched function signatures
3. Follow the change through the entire call stack - From entry points to helper functions to error handling
4. Verify consistency before presenting - Check that all related code reflects the new design

Examples of consistency failures to avoid:
- Changing what a function does but not updating its documentation
- Updating function parameters but missing some call sites
- Changing error conditions but not updating error messages
- Modifying data structures but leaving old field names in comments

Verification checklist:
- Do all error messages match what's actually being checked?
- Do all function signatures match their calls?
- Do all comments reflect current behavior?
- Are all related files updated consistently?

## Design and Development

**IMPORTANT**: When writing any code, always follow the "Workflow" sections below (in order of appearance).

### Design Discussion Workflow

When discussing new features or how to fixing complex issues:
- Clearly define the problem/feature before writing code
- List specific, verifiable assumptions
- Define acceptance criteria upfront
- Ask clarifying questions until the problem is well understood
- Document the problem definition before proposing solutions
- Wait until the user confirms they are ready to end the Design Discussion before moving on

### Propose Solution Workflow

When proposing solutions to defined problems:
- Start from a clear problem definition
- Propose multiple potential solutions when appropriate
- Compare solutions based on:
  - Pros and cons
  - Adherence to KISS, DRY, YAGNI principles
  - Performance implications
  - Scalability concerns
  - Maintainability and readability
  - Security considerations
  - Development effort
- Evaluate solutions by analyzing risks and potential impacts
- Consider "What could go wrong?" for each approach
- Justify solution selection based on systematic comparison
- Use visual aids (diagrams, flowcharts) when helpful for complex solutions

### Code Implementation Workflow

**IMPORTANT**: Always follow this approach when writing any code.

When implementing code changes:
- Follow all coding standards in this file at all times
- Maintain a todo list to stay organized
- Maintain a `design.md` file in the project base directory covering:
  - Overview
  - Architecture
  - Important design decisions
- Use virtual environment `.venv` in the git repo root for Python changes
- When fixing tests, only run the failing tests during iteration
- Update `design.md` immediately after making significant code changes
- Follow all rules in the "Code Quality & Linting" sub-section earlier in this file
- Finish by asking the user if they want unit test written per the rules in the "Unit Tests" sub-section earlier in this file

### Code Review Workflow

When reviewing code changes:
- Act as an expert software engineer with deep knowledge of medical devices and ISO 62304/TIR 45
- Evaluate changes in context of the existing codebase
- Understand how modified code interacts with surrounding logic and related files

#### Required Output Format for Each Finding

Every issue identified must include:
1. **File Path**: Absolute path to the file
2. **Line Numbers**: Specific line or line range (e.g., lines 45-52)
3. **Code Snippet**: The actual problematic code (max 10 lines)
4. **Problem Statement**: What is wrong and why it's a problem
5. **Impact**: Specific consequences if left unfixed
6. **Considerations**: Key factors to consider when fixing (NOT a prescribed solution)

Example format:
CRITICAL-001: Unvalidated Input in Hash Function
File: /path/to/algorithms.py:32-36
Current Code:
    def calculateScenarioStepsHash(scenarioLines):
      import hashlib
      stepsContent = '\n'.join(scenarioLines)
      return hashlib.sha256(stepsContent.encode('utf-8')).hexdigest()

Problem: Function accepts scenarioLines without validating:
- Could be None causing AttributeError in join()
- Could be non-list type causing TypeError
- Could contain non-string elements causing join() failure
- No indication whether empty input is valid business case

Impact:
- Application crashes with unclear errors
- Potential data corruption if invalid hashes stored
- Silent failures could corrupt database hash values

Considerations for Fix:
- Determine if empty scenarios are valid (should hash or error?)
- Decide if non-string elements should be converted or rejected
- Ensure error messages help diagnose root cause

#### Assessment Categories

For each category, provide findings in the above format:

- **Design & Architecture**:
  - Verify: Changes fit existing patterns, avoid coupling, enforce separation of concerns, align with module boundaries
  - Output: Specific module dependencies that violate boundaries with import statements

- **Complexity & Maintainability**:
  - Ensure: Flat control flow, low cyclomatic complexity (cite specific value), DRY violations (show duplicate code), dead code (unreachable lines)
  - Output: Functions exceeding 50 lines or cyclomatic complexity > 10 with specific measurements

- **Functionality & Correctness**:
  - Confirm: Input validation gaps (show missing checks), uncaught exceptions (show try blocks without handlers), non-idempotent operations
  - Output: Exact conditions that cause failures with example inputs

- **Readability & Naming**:
  - Check: Variable names not following conventions (show actual vs expected), misleading comments (show comment vs actual code)
  - Output: Side-by-side comparison of current vs recommended names

- **Best Practices & Patterns**:
  - Validate: SOLID violations (show specific principle violated), missing resource cleanup (show open without close), inconsistent patterns
  - Output: Pattern used elsewhere in codebase vs current implementation

- **Test Coverage & Quality**:
  - Verify: Missing test cases (list specific scenarios), inappropriate mocks (show what should be tested instead)
  - Output: Specific test function that should exist with skeleton implementation

- **Documentation & Comments**:
  - Confirm: Missing docstrings (list functions without), outdated comments (show comment vs current implementation)
  - Output: Required docstring format with populated fields

- **Security & Compliance**:
  - Check: Input validation (show exact regex/validation needed), SQL injection risks (show parameterization needed), path traversal (show sanitization needed)
  - Output: Vulnerable code with security requirements

- **Performance & Scalability**:
  - Identify: N+1 queries (show loop with query), unbounded memory (show accumulation without limit), blocking I/O (show async opportunity)
  - Output: Benchmark comparison or complexity analysis

- **Observability & Logging**:
  - Verify: Missing log statements (show where to add), wrong log levels (show current vs correct level), exposed sensitive data
  - Output: Exact log statement to add with proper formatting

#### Severity Classification

Prioritize issues with clear criteria:
- **Critical**: Data loss, security vulnerability, or compliance violation - requires immediate fix
- **Major**: Functionality broken, performance degradation >50%, or maintenance blocker
- **Minor**: Style violations, missing documentation, or performance impact <10%
- **Enhancement**: Optional improvements for better practices

#### Review Output Structure

Structure the complete review as:
1. Executive Summary (2-3 sentences)
2. Statistics (files reviewed, issues found by severity)
3. Critical Issues (if any) - each with full Required Output Format
4. Major Issues (if any) - each with full Required Output Format
5. Minor Issues - summarized with file:line references
6. Enhancements - optional improvements

#### Actionability Requirement

Each finding must be self-contained such that a developer can:
1. Navigate to the exact location
2. Understand the issue without additional context
3. Make an informed decision about how to fix it
4. Verify the fix addresses the issue

If additional context is needed, provide:
- Reference to similar patterns in the codebase
- Link to specific design document section that explains requirements
