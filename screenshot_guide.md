# Screenshot Capture Guide for QuickGigs Design Documentation

This guide will help you capture all the screenshots needed for your `design.md` file.

## Prerequisites

1. **Django server running**: Make sure your Django development server is running on `http://localhost:8000`
2. **Browser with screenshot capabilities**: Chrome, Firefox, or Safari with screenshot extensions
3. **Screenshot tool**: Use browser extensions like:
   - **Chrome**: "Full Page Screen Capture" or "Nimbus Screenshot"
   - **Firefox**: "FireShot" or "Nimbus Screenshot"
   - **Safari**: Built-in screenshot tool (Cmd+Shift+4)

## Screenshot Categories

### 1. Live Application Screenshots (from Django app)

These should be captured from your actual running Django application:

#### Homepage & Navigation
- **File**: `docs/screenshots/design/quickgigs-homepage-hero.png`
- **URL**: `http://localhost:8000/`
- **Description**: Homepage showing hero section, navigation, and featured gigs

- **File**: `docs/screenshots/design/navigation-role-based.png`
- **URL**: `http://localhost:8000/accounts/login/`
- **Description**: Login page showing navigation structure

#### Gig Management
- **File**: `docs/screenshots/design/gig-list-showcase.png`
- **URL**: `http://localhost:8000/gigs/`
- **Description**: Gig listing page with cards and filtering

- **File**: `docs/screenshots/design/gig-detail-page.png`
- **URL**: `http://localhost:8000/gigs/1/` (if gig exists)
- **Description**: Individual gig detail page with application form

#### Dashboards
- **File**: `docs/screenshots/design/employer-dashboard-interface.png`
- **URL**: `http://localhost:8000/gigs/my-gigs/`
- **Description**: Employer dashboard showing posted gigs

- **File**: `docs/screenshots/design/freelancer-dashboard.png`
- **URL**: `http://localhost:8000/gigs/my-applications/`
- **Description**: Freelancer dashboard showing applications

### 2. Demo Page Screenshots

These can be captured from the demo pages we created:

#### Design System
- **File**: `docs/screenshots/design/color-palette-system.png`
- **URL**: `file:///path/to/quickgigs-django/demo_pages/design-system/colors/index.html`
- **Description**: Color system showing primary, semantic, and neutral palettes

- **File**: `docs/screenshots/design/typography-hierarchy.png`
- **URL**: `file:///path/to/quickgigs-django/demo_pages/design-system/typography/index.html`
- **Description**: Typography scale showing heading sizes and responsive behavior

- **File**: `docs/screenshots/design/component-library-showcase.png`
- **URL**: `file:///path/to/quickgigs-django/demo_pages/design-system/components/index.html`
- **Description**: Component library with atomic design structure

#### Comparisons & Flows
- **File**: `docs/screenshots/design/before-after-comparison.png`
- **URL**: `file:///path/to/quickgigs-django/demo_pages/comparison/index.html`
- **Description**: Side-by-side comparison of todo app vs QuickGigs

- **File**: `docs/screenshots/design/payment-flow-journey.png`
- **URL**: `file:///path/to/quickgigs-django/demo_pages/payment-flow/index.html`
- **Description**: Payment flow steps from trigger to success

- **File**: `docs/screenshots/design/stripe-checkout-integration.png`
- **URL**: `file:///path/to/quickgigs-django/demo_pages/stripe/index.html`
- **Description**: Stripe checkout interface and success states

#### Performance & Analytics
- **File**: `docs/screenshots/design/performance-lighthouse-scores.png`
- **URL**: `file:///path/to/quickgigs-django/demo_pages/performance-demo/index.html`
- **Description**: Lighthouse performance metrics

- **File**: `docs/screenshots/design/business-metrics-analytics.png`
- **URL**: `file:///path/to/quickgigs-django/demo_pages/analytics-demo/index.html`
- **Description**: Business metrics dashboard

#### Testing & Accessibility
- **File**: `docs/screenshots/testing/test-execution-overview.png`
- **URL**: `file:///path/to/quickgigs-django/demo_pages/testing-demo/index.html`
- **Description**: Test execution results

- **File**: `docs/screenshots/design/accessibility-features.png`
- **URL**: `file:///path/to/quickgigs-django/demo_pages/accessibility-demo/index.html`
- **Description**: Accessibility features demo

### 3. Manual Screenshots (from your existing files)

You already have some testing screenshots that can be used:

- **File**: `docs/screenshots/quickgigs/testing/all_tests_after.png` → Copy to `docs/screenshots/testing/test-execution-overview.png`
- **File**: `docs/screenshots/quickgigs/testing/basic_tests.png` → Use for testing documentation
- **File**: `docs/screenshots/quickgigs/testing/payments test models.png` → Use for payment testing documentation

## Step-by-Step Capture Process

### Step 1: Capture Live Application Screenshots

1. **Start your Django server**:
   ```bash
   python manage.py runserver
   ```

2. **Open your browser** and navigate to each URL listed above

3. **Take full-page screenshots** using your browser's screenshot tool

4. **Save screenshots** to the correct paths in `docs/screenshots/`

### Step 2: Capture Demo Page Screenshots

1. **Open demo pages** in your browser:
   ```bash
   # Navigate to the demo_pages directory and open index.html files
   open demo_pages/design-system/colors/index.html
   open demo_pages/design-system/typography/index.html
   # ... etc
   ```

2. **Take screenshots** of each demo page

3. **Save screenshots** to the correct paths

### Step 3: Copy Existing Screenshots

1. **Copy your existing testing screenshots** to the appropriate locations
2. **Rename files** as needed to match the expected filenames

### Step 4: Create Missing Screenshots

For screenshots that don't fit the above categories, you can:

1. **Use design tools** like Figma, Sketch, or draw.io to create diagrams
2. **Take screenshots** of your code editor showing specific code examples
3. **Create mockups** using tools like Canva or similar

## Screenshot Quality Guidelines

- **Resolution**: Minimum 1920x1080 for desktop screenshots
- **Format**: PNG for best quality
- **File size**: Keep under 2MB per screenshot
- **Consistency**: Use same browser and zoom level for similar screenshots
- **Clarity**: Ensure text is readable and UI elements are clear

## Quick Commands

```bash
# Start Django server
python manage.py runserver

# Open demo pages in browser
open demo_pages/design-system/colors/index.html
open demo_pages/design-system/typography/index.html
open demo_pages/comparison/index.html

# Copy existing screenshots
cp docs/screenshots/quickgigs/testing/all_tests_after.png docs/screenshots/testing/test-execution-overview.png
```

## Troubleshooting

### Django Server Issues
- Make sure the server is running on port 8000
- Check for any error messages in the terminal
- Ensure all migrations are applied

### Screenshot Quality Issues
- Use browser zoom to 100% for consistent sizing
- Disable browser extensions that might interfere
- Use incognito/private browsing mode for clean screenshots

### File Path Issues
- Ensure the `docs/screenshots/` directory structure exists
- Use absolute paths if relative paths don't work
- Check file permissions

## Next Steps

After capturing all screenshots:

1. **Update design.md**: Remove placeholder comments
2. **Verify all images load**: Check that all screenshots display correctly
3. **Optimize images**: Compress if needed while maintaining quality
4. **Test documentation**: Ensure the design.md file renders properly

## Automation Script

If you want to automate this process in the future, you can use the `generate_screenshots.py` script we created, but you'll need to:

1. Install ChromeDriver: `brew install chromedriver`
2. Fix the Chrome driver issues we encountered
3. Run the script: `python generate_screenshots.py`

For now, manual capture will give you the best quality and control over the screenshots. 