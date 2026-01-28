# Makefile-style commands for Price Tracker

# Colors for output
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"

function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Help command
function Show-Help {
    Write-ColorOutput $Green "🚀 Price Tracker Bénin - Commands"
    Write-Host ""
    Write-Host "Setup:"
    Write-Host "  .\dev.ps1 setup          - Initial setup (create .env, etc.)"
    Write-Host "  .\dev.ps1 install        - Install dependencies"
    Write-Host ""
    Write-Host "Docker:"
    Write-Host "  .\dev.ps1 up             - Start all services"
    Write-Host "  .\dev.ps1 down           - Stop all services"
    Write-Host "  .\dev.ps1 restart        - Restart all services"
    Write-Host "  .\dev.ps1 rebuild        - Rebuild and restart"
    Write-Host "  .\dev.ps1 logs [service] - Show logs"
    Write-Host ""
    Write-Host "Database:"
    Write-Host "  .\dev.ps1 migrate        - Run database migrations"
    Write-Host "  .\dev.ps1 migration      - Create new migration"
    Write-Host "  .\dev.ps1 db-shell       - Access MySQL shell"
    Write-Host ""
    Write-Host "Development:"
    Write-Host "  .\dev.ps1 shell          - Access backend shell"
    Write-Host "  .\dev.ps1 test           - Run tests"
    Write-Host "  .\dev.ps1 test-scraper   - Test Jumia scraper"
    Write-Host ""
    Write-Host "Utils:"
    Write-Host "  .\dev.ps1 clean          - Clean containers and volumes"
    Write-Host "  .\dev.ps1 status         - Show services status"
    Write-Host "  .\dev.ps1 help           - Show this help"
}

# Setup
function Setup {
    Write-ColorOutput $Green "📦 Setting up Price Tracker..."
    
    if (!(Test-Path .env)) {
        Copy-Item .env.example .env
        Write-ColorOutput $Yellow "⚠️  .env created from .env.example - Please update with your values!"
    }
    
    Write-ColorOutput $Green "✅ Setup complete!"
}

# Start services
function Start-Services {
    Write-ColorOutput $Green "🚀 Starting services..."
    docker-compose up -d
    Start-Sleep -Seconds 5
    docker-compose ps
}

# Stop services
function Stop-Services {
    Write-ColorOutput $Yellow "🛑 Stopping services..."
    docker-compose down
}

# Restart services
function Restart-Services {
    Write-ColorOutput $Yellow "🔄 Restarting services..."
    docker-compose restart
    docker-compose ps
}

# Rebuild
function Rebuild-Services {
    Write-ColorOutput $Yellow "🔨 Rebuilding services..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    docker-compose ps
}

# Show logs
function Show-Logs {
    param($Service)
    if ($Service) {
        docker-compose logs -f $Service
    } else {
        docker-compose logs -f
    }
}

# Run migrations
function Run-Migrations {
    Write-ColorOutput $Green "📊 Running database migrations..."
    docker-compose exec backend alembic upgrade head
    Write-ColorOutput $Green "✅ Migrations complete!"
}

# Create migration
function Create-Migration {
    $msg = Read-Host "Migration message"
    Write-ColorOutput $Green "📝 Creating migration: $msg"
    docker-compose exec backend alembic revision --autogenerate -m "$msg"
}

# Database shell
function DB-Shell {
    Write-ColorOutput $Green "💾 Accessing MySQL shell..."
    docker-compose exec mysql mysql -u price_user -pprice_password price_tracker
}

# Backend shell
function Backend-Shell {
    Write-ColorOutput $Green "🐚 Accessing backend shell..."
    docker-compose exec backend bash
}

# Run tests
function Run-Tests {
    Write-ColorOutput $Green "🧪 Running tests..."
    docker-compose exec backend pytest -v
}

# Test scraper
function Test-Scraper {
    Write-ColorOutput $Green "🔍 Testing Jumia scraper..."
    $url = Read-Host "Enter Jumia product URL (or press Enter for default test)"
    
    docker-compose exec backend python -c @"
import asyncio
from app.services.scraper.jumia_scraper import JumiaScraper

async def test():
    url = '$url' if '$url' else 'https://www.jumia.com.bj/'
    async with JumiaScraper() as scraper:
        print(f'Testing: {url}')
        data = await scraper.scrape_product(url)
        if data:
            print(f'✅ Name: {data.get(\"name\")}')
            print(f'💰 Price: {data.get(\"price\")} {data.get(\"currency\")}')
        else:
            print('❌ Scraping failed')

asyncio.run(test())
"@
}

# Clean
function Clean-All {
    Write-ColorOutput $Red "🧹 Cleaning containers and volumes..."
    $confirm = Read-Host "This will delete all data. Continue? (yes/no)"
    if ($confirm -eq "yes") {
        docker-compose down -v
        Write-ColorOutput $Green "✅ Cleaned!"
    } else {
        Write-ColorOutput $Yellow "Cancelled."
    }
}

# Status
function Show-Status {
    Write-ColorOutput $Green "📊 Services Status:"
    docker-compose ps
    Write-Host ""
    Write-ColorOutput $Green "🌐 URLs:"
    Write-Host "  Backend API: http://localhost:8000"
    Write-Host "  Swagger UI:  http://localhost:8000/docs"
}

# Main switch
switch ($args[0]) {
    "setup" { Setup }
    "up" { Start-Services }
    "down" { Stop-Services }
    "restart" { Restart-Services }
    "rebuild" { Rebuild-Services }
    "logs" { Show-Logs $args[1] }
    "migrate" { Run-Migrations }
    "migration" { Create-Migration }
    "db-shell" { DB-Shell }
    "shell" { Backend-Shell }
    "test" { Run-Tests }
    "test-scraper" { Test-Scraper }
    "clean" { Clean-All }
    "status" { Show-Status }
    "help" { Show-Help }
    default { Show-Help }
}
