# Cloudinary Image Upload Setup Guide

## ✅ Changes Made

1. **Updated `JCBPart` model** - Changed `image_360_base` from `ImageField` to `CloudinaryField`
2. **Created migration** - `0006_alter_jcbpart_image_360_base.py` for the model change
3. **Secured credentials** - Moved Cloudinary API keys to environment variables in `settings.py`
4. **Added `.env.example`** - Template for environment variables

## 🔧 Setup Instructions

### Step 1: Install python-dotenv (if not already installed)
```bash
pip install python-dotenv
```

### Step 2: Create `.env` file in project root
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### Step 3: Add your Cloudinary credentials to `.env`
1. Go to [Cloudinary Console](https://cloudinary.com/console/settings)
2. Copy your `Cloud Name`, `API Key`, and `API Secret`
3. Update `.env`:
```
CLOUDINARY_CLOUD_NAME=your_actual_cloud_name
CLOUDINARY_API_KEY=your_actual_api_key
CLOUDINARY_API_SECRET=your_actual_api_secret
```

### Step 4: Update `core/settings.py` to load `.env`
Add at the very top of `core/settings.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Step 5: Run migrations
```bash
python manage.py migrate
```

### Step 6: Test image upload
1. Go to admin panel or inventory page
2. Upload an image via the form
3. Image should now be stored on Cloudinary

## 📦 Required Packages (in requirements.txt)
- `cloudinary` ✅
- `django-cloudinary-storage` ✅
- `python-dotenv` (add if missing)

## 🐛 Troubleshooting

### Issue: "Cloudinary credentials not found"
**Solution:** Ensure `.env` file exists and `load_dotenv()` is called in settings.py

### Issue: "Image upload still shows local path"
**Solution:** Run `python manage.py migrate` to apply the new migration

### Issue: "OLD images not showing"
**Solution:** Old images stored locally won't show. You need to:
1. Re-upload them to Cloudinary, OR
2. Manually migrate them using Cloudinary's API

### Issue: "403 Forbidden errors"
**Solution:** Check that your API credentials in `.env` are correct

## 📝 Environment Setup for Production

For **Render.com** or **Heroku**:
1. Go to your deployment dashboard
2. Add environment variables:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

For **Vercel**:
Add to `vercel.json` or environment settings:
```json
{
  "env": {
    "CLOUDINARY_CLOUD_NAME": "@your-cloud-name",
    "CLOUDINARY_API_KEY": "@your-api-key",
    "CLOUDINARY_API_SECRET": "@your-api-secret"
  }
}
```

## ✨ Features You Now Have

- ✅ Images stored on Cloudinary (not local disk)
- ✅ Automatic image optimization
- ✅ CDN delivery (faster loading worldwide)
- ✅ Secure credentials with environment variables
- ✅ Both `DaftarBarang` and `JCBPart` using Cloudinary

## 📚 Files Modified

1. `data/models.py` - Changed `ImageField` to `CloudinaryField`
2. `data/migrations/0006_alter_jcbpart_image_360_base.py` - New migration
3. `core/settings.py` - Use environment variables for Cloudinary config
4. `.env.example` - Created template for environment variables

---

**Next Step:** Run migrations and test uploading an image!
