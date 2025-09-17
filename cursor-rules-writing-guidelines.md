Cursor Rules Writing Guidelines
Concise guidelines based on PatrickJS/awesome-cursorrules and official Cursor documentation.

Basic Format
Each .cursorrules or .mdc file must include:

---
description: Brief description of the file's purpose
globs: File matching patterns
---

Rule content



Rule Writing Principles


Language: Write all cursor rules in English for consistency and global accessibility

Action Words: Start with simple action words: Must, Use, Never, Ensure, Implement, Avoid

Format: One rule per line, starting with -

Specificity: Rules should be specific and directly guide code generation

Clarity: Avoid abstract concepts and theoretical descriptions

Examples: Include both correct and incorrect code examples when applicable


Action Words Usage Guidelines

Standard Action Words



Action Word
Usage Scenario
Strength
Example




Must
Mandatory requirements, critical rules
Strict
Must annotate entity classes with @Entity


Use
Preferred approaches, recommended practices
Standard
Use @GeneratedValue for primary keys


Never
Absolute prohibitions, security/correctness
Absolute
Never expose passwords in logs


Ensure
Verification requirements, quality gates
Validation
Ensure all endpoints have validation


Implement
Implementation requirements, patterns
Structural
Implement repository pattern for data access


Avoid
Best practices, quality recommendations
Advisory
Avoid deep nesting beyond 3 levels




Usage Decision Tree


Security/Correctness Issues → Use Never


Mandatory Requirements → Use Must


Recommended Practices → Use Use


Quality Improvements → Use Avoid


Validation Requirements → Use Ensure


Architecture Patterns → Use Implement



Good Rule Examples

- Must annotate entity classes with @Entity
- Use @GeneratedValue for primary keys
- Never expose passwords in logs
- Ensure all endpoints have validation
- Implement repository pattern for data access
- Avoid deep nesting beyond 3 levels



Examples to Avoid

- Code should follow best practices (too abstract)
- Performance should be good (no specific metrics)
- Must go through code review (non-technical requirement)
- Don't use deep nesting (use standard action words)
- Try to avoid magic numbers (use standard action words)



Language Standards

English First
All cursor rules should be written in English to ensure:


Global accessibility: Developers worldwide can understand and contribute

Consistency: Uniform documentation across all languages and teams

Tool compatibility: Better integration with English-based development tools

Community collaboration: Easier knowledge sharing and maintenance


Content Language Requirements


Rule descriptions: Write in clear, professional English

Code comments: Use English for all code examples and comments

Variable names: Use English words in code samples

Documentation: All explanatory text should be in English


Exceptions


Technical terms: Industry-standard terms may remain in original language if widely recognized

Brand names: Keep proper nouns and brand names as-is

Legacy code: When showing existing code examples, maintain original language but add English explanations


File Naming
Use kebab-case naming:

java-entity-rules.mdc
react-component-rules.mdc
api-security-rules.mdc


Globs Patterns
Target specific file types:

# Java entity classes
globs: **/entity/*.java, **/entities/*.java

# React components
globs: **/components/**/*.tsx

# API controllers
globs: **/controller/*.java, **/api/*.java



Conditional Rules
Use conditional expressions when needed:

- Use @Data from Lombok, unless specified otherwise
- Apply @Valid for validation, except for simple GET requests



Example File

---
description: Java entity class conventions
globs: **/entity/*.java, **/entities/*.java
---

# Java Entity Class Rules

## Basic Annotations
- Must annotate with @Entity and @Table
- Use @Id and @GeneratedValue for primary keys
- Apply @Column(nullable = false) for required fields

## Performance Guidelines
- Never use FetchType.EAGER for collections
- Use @OneToMany(fetch = FetchType.LAZY) for large datasets

## Security Practices
- Use @JsonIgnore for sensitive fields like passwords
- Apply @Column(length = 255) to limit string field sizes

## Example Implementation

```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, length = 100)
    private String username;
    
    @JsonIgnore
    @Column(nullable = false)
    private String password;
}