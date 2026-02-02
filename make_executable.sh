#!/bin/bash

# Make all scripts executable
chmod +x backend/run_backend.sh 2>/dev/null
chmod +x backend/test_backend.sh 2>/dev/null
chmod +x backend/setup_garuda.sh 2>/dev/null
chmod +x frontend/run_frontend.sh 2>/dev/null
chmod +x run_all.sh
chmod +x run_backend.sh
chmod +x test_all.sh
chmod +x test_backend.sh
chmod +x test_full_stack.sh

echo "✅ All scripts are now executable"
