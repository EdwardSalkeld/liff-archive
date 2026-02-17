.PHONY: help dev build build-local install install-hugo install-playwright test test-update test-html ci-build ci-test clean

# Default target - show help
.DEFAULT_GOAL := help

##@ General

help: ## Display this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

dev: ## Start development server with Docker
	docker-compose up website

##@ Build

build: ## Build Hugo site with Docker
	docker-compose run --rm hugo_build

build-local: ## Build Hugo site locally (requires Hugo installed)
	cd hugo && hugo

##@ Dependencies

install: install-hugo install-playwright ## Install all dependencies (Hugo and Playwright)

install-hugo: ## Install Hugo (for CI environments)
	@echo "Hugo installation should be done via system package manager or GitHub Actions"
	@echo "See: https://gohugo.io/installation/"
	@which hugo > /dev/null 2>&1 && echo "✓ Hugo is already installed: $$(hugo version)" || echo "✗ Hugo is not installed"

install-playwright: ## Install Playwright browsers
	npm ci
	npx playwright install --with-deps chromium

##@ Testing

test: ## Run Playwright visual regression tests
	npm test

test-update: ## Update Playwright snapshot baselines
	npm run test:update

test-html: build-local ## Run HTML validation tests (requires local build)
	chmod +x .github/workflows/test-html.sh
	.github/workflows/test-html.sh

##@ CI/CD

ci-build: build-local ## Build for CI (same as build-local)

ci-test: test-html test ## Run all tests for CI (HTML validation + Playwright)

##@ Cleanup

clean: ## Clean build artifacts
	rm -rf hugo/public
	rm -rf hugo/.hugo_build.lock
	rm -rf playwright-report
	rm -rf test-results
