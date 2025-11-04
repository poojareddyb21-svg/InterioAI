# InterioAI Backend - Simple Setup Guide

**Just 2 files! No AI - Only user data storage**

---

## 📦 FILES PROVIDED

### 1. app.py
- User authentication (signup/login)
- User data storage
- Design data storage
- SQLite database
- **NO AI integration** (your friend will handle that)

### 2. requirements.txt
- Only essential dependencies
- Flask, CORS, SQLite

---

## 🚀 QUICK SETUP

### Step 1: Create Folder
```bash
mkdir InterioAI-Backend
cd InterioAI-Backend
```

### Step 2: Copy Files
Copy these 2 files into the folder:
- `app.py`
- `requirements.txt`

### Step 3: Install & Run
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run backend
python app.py
```

**Backend runs at:** `http://localhost:5000`

---

## 📤 PUSH TO GITHUB

```bash
# Initialize git
git init

# Add .gitignore
echo "venv/
__pycache__/
*.pyc
*.db
.DS_Store" > .gitignore

# Commit
git add .
git commit -m "Backend for InterioAI - User data storage only"

# Push
git remote add origin https://github.com/YOUR-USERNAME/InterioAI-Backend.git
git push -u origin main
```

---

## 🧪 TEST ENDPOINTS

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Signup
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@test.com","password":"123456"}'
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"123456"}'
```

### Save Design
```bash
curl -X POST http://localhost:5000/api/designs \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "room_type": "Bedroom",
    "style": "Modern",
    "palette": "lightblue",
    "furniture": "bed, desk",
    "width": "5-8m",
    "length": "8-10m"
  }'
```

### Get Designs
```bash
curl http://localhost:5000/api/designs/1
```

---

## 📋 API ENDPOINTS

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/auth/signup` | POST | Register user |
| `/api/auth/login` | POST | Login user |
| `/api/users/{id}` | GET | Get user info |
| `/api/users/{id}` | PUT | Update user |
| `/api/designs` | POST | Save design |
| `/api/designs/{user_id}` | GET | Get user designs |
| `/api/designs/{id}` | DELETE | Delete design |

---

## 🌐 DEPLOY ON RENDER

1. **Push to GitHub** (see above)

2. **Go to Render.com**
   - Sign up with GitHub
   - Click "New" → "Web Service"
   - Select your repository

3. **Configure**
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn -w 4 -b 0.0.0.0:5000 app:app`

4. **Deploy**
   - Wait 2-3 minutes
   - Get your URL: `https://your-app.onrender.com`

---

## 🔗 FRONTEND INTEGRATION

Add this to your `InterioAI.html`:

```javascript
// API URL
const API_URL = 'http://localhost:5000/api'; // Local
// const API_URL = 'https://your-backend-url.onrender.com/api'; // Production

// Login
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.querySelector('#loginForm input[type="email"]').value;
    const password = document.querySelector('#loginForm input[type="password"]').value;
    
    try {
        const response = await fetch(API_URL + '/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('user_name', data.user.name);
            goToDashboard();
            alert('✅ Login successful!');
        } else {
            alert('❌ ' + data.error);
        }
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

// Signup
async function handleSignup(event) {
    event.preventDefault();
    
    const name = document.querySelector('#signupForm input[type="text"]').value;
    const email = document.querySelector('#signupForm input[type="email"]').value;
    const password = document.querySelector('#signupForm input[type="password"]').value;
    
    try {
        const response = await fetch(API_URL + '/auth/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ Account created! Please login.');
            toggleAuthForms();
        } else {
            alert('❌ ' + data.error);
        }
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

// Save Design
async function handleDesignSubmit(event) {
    event.preventDefault();
    
    const user_id = localStorage.getItem('user_id');
    if (!user_id) {
        alert('Please login first');
        return;
    }
    
    const formData = new FormData(event.target);
    
    try {
        const response = await fetch(API_URL + '/designs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: parseInt(user_id),
                room_type: formData.get('roomType'),
                style: formData.get('style'),
                palette: formData.get('palette'),
                furniture: formData.get('furniture'),
                width: formData.get('width'),
                length: formData.get('length')
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ Design saved!');
            loadDesigns();
        } else {
            alert('❌ ' + data.error);
        }
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

// Load Designs
async function loadDesigns() {
    const user_id = localStorage.getItem('user_id');
    if (!user_id) return;
    
    try {
        const response = await fetch(API_URL + `/designs/${user_id}`);
        const data = await response.json();
        
        if (data.success) {
            displayDesigns(data.designs);
        }
    } catch (error) {
        console.error('Error loading designs:', error);
    }
}

// Display Designs
function displayDesigns(designs) {
    const container = document.getElementById('previousDesigns');
    if (!container) return;
    
    container.innerHTML = '';
    
    designs.forEach(design => {
        const div = document.createElement('div');
        div.className = 'previous-item';
        div.innerHTML = `
            <div style="background: ${design.palette}; height: 180px; border-radius: 0.6rem; margin-bottom: 0.8rem; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                ${design.room_type}
            </div>
            <strong>${design.room_type} - ${design.style}</strong>
            <small>${new Date(design.created_at).toLocaleDateString()}</small>
            <p>🛋️ ${design.furniture || 'No furniture'}</p>
            <p>📏 ${design.width} x ${design.length}</p>
        `;
        container.appendChild(div);
    });
}
```

---

## 🎯 WHAT YOUR FRIEND WILL ADD

Your friend will add AI endpoints for design recommendations.

They should:
1. Clone your backend repo
2. Add their AI code to `app.py`
3. Add AI routes like `/api/ai/recommend`
4. Test and deploy

---

## ✅ FOLDER STRUCTURE

```
InterioAI-Backend/
├── app.py              # Backend code
├── requirements.txt    # Dependencies
├── .gitignore         # (create this)
└── interioai.db       # (auto-created, don't commit)
```

---

## 💡 KEY FEATURES

✅ User registration and login
✅ Password hashing (secure)
✅ Design data storage
✅ SQLite database (no setup needed)
✅ CORS enabled for frontend
✅ Error handling
✅ Ready for deployment
✅ Simple 2-file setup

**NO AI** - Your friend will add that!

---

## 🆘 TROUBLESHOOTING

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "Port already in use"
Change port in `app.py`:
```python
app.run(port=8000)
```

### "Can't connect from frontend"
- Check backend is running
- Verify API_URL matches
- Check CORS is enabled (it is)

---

## 📞 SHARE WITH YOUR FRIEND

**Backend Repository:**
```
https://github.com/YOUR-USERNAME/InterioAI-Backend
```

**Tell them:**
- Backend stores user data and designs
- API endpoints are ready to use
- They can add AI routes to the same `app.py`
- Database has User and Design tables

---

## ✨ DONE!

You have:
- ✅ Simple 2-file backend
- ✅ User data storage
- ✅ Design data storage
- ✅ Ready for GitHub
- ✅ Easy to deploy
- ✅ No AI (friend will add)

**Push to GitHub and share with your friend!** 🚀

