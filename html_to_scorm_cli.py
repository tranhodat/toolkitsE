#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTML to SCORM Converter - Command Line Tool
Chuyển đổi file HTML sang định dạng SCORM 1.2 & 2004
"""

import os
import sys
import argparse
import zipfile
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
import uuid

def escape_xml(text):
    """Escape XML special characters"""
    if not text:
        return ""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;"))

def read_html_file(filepath):
    """Read HTML file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Lỗi đọc file: {e}")
        return None

def create_scorm_wrapper(html_content, scorm_version="1.2"):
    """Create SCORM wrapper for HTML"""
    
    if scorm_version == "1.2":
        scorm_script = """<script>
// SCORM 1.2 API Implementation
var apiAdapter = {
    cmi: {
        core: { score: { raw: 0 }, lesson_status: "not attempted" },
        suspend_data: "",
        launch_data: ""
    },
    
    initialize: function() {
        console.log("SCORM 1.2 Initialized");
        return "true";
    },
    
    finish: function() {
        this.cmi.core.lesson_status = "completed";
        console.log("SCORM 1.2 Finished - Status: completed");
        return "true";
    },
    
    setValue: function(key, value) {
        console.log(`SCORM Set: ${key} = ${value}`);
        return "true";
    },
    
    getValue: function(key) {
        console.log(`SCORM Get: ${key}`);
        return "";
    },
    
    commit: function() {
        console.log("SCORM Data Committed");
        return "true";
    }
};

// Initialize on load
window.addEventListener("load", function() {
    apiAdapter.initialize();
});

// Mark as completed on before unload
window.addEventListener("beforeunload", function() {
    if (document.readyState !== "loading") {
        apiAdapter.finish();
    }
});

// Expose to global scope
window.API = apiAdapter;
</script>"""
    else:  # SCORM 2004
        scorm_script = """<script>
// SCORM 2004 4th Edition API Implementation
var apiAdapter = {
    cmi: {
        core: { score: { raw: 0 }, completion_status: "incomplete" },
        interactions: [],
        objectives: []
    },
    
    initialize: function() {
        console.log("SCORM 2004 Initialized");
        return "true";
    },
    
    terminate: function() {
        this.cmi.core.completion_status = "completed";
        console.log("SCORM 2004 Terminated - Status: completed");
        return "true";
    },
    
    setValue: function(key, value) {
        console.log(`SCORM Set: ${key} = ${value}`);
        return "true";
    },
    
    getValue: function(key) {
        console.log(`SCORM Get: ${key}`);
        return "";
    },
    
    commit: function() {
        console.log("SCORM Data Committed");
        return "true";
    }
};

// Initialize on load
window.addEventListener("load", function() {
    apiAdapter.initialize();
});

// Mark as completed on before unload
window.addEventListener("beforeunload", function() {
    if (document.readyState !== "loading") {
        apiAdapter.terminate();
    }
});

// Expose to global scope
window.API_1484_11 = apiAdapter;
</script>"""
    
    # Extract body content
    body_match = None
    head_content = ""
    
    import re
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.IGNORECASE | re.DOTALL)
    body_content = body_match.group(1) if body_match else html_content
    
    head_match = re.search(r'<head[^>]*>(.*?)</head>', html_content, re.IGNORECASE | re.DOTALL)
    head_content = head_match.group(1) if head_match else ""
    
    wrapped_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SCORM Course</title>
    {head_content}
    <style>
        .scorm-indicator {{
            position: fixed;
            top: 10px;
            right: 10px;
            background: #10b981;
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            z-index: 9999;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="scorm-indicator">✓ SCORM {scorm_version} Active</div>
    {body_content}
    {scorm_script}
</body>
</html>"""
    
    return wrapped_html

def create_manifest(course_id, course_title, course_desc, version, scorm_version, max_score):
    """Create imsmanifest.xml"""
    
    if scorm_version == "2004":
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="{escape_xml(course_id)}" version="{escape_xml(version)}" 
    xmlns="http://www.imsglobal.org/xsd/imscp_v1p2" 
    xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_v1p2" 
    xmlns:adlseq="http://www.adlnet.org/xsd/adlseq_v1p2" 
    xmlns:adlnav="http://www.adlnet.org/xsd/adlnav_v1p2" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p2 imscp_v1p2.xsd 
        http://www.adlnet.org/xsd/adlcp_v1p2 adlcp_v1p2.xsd 
        http://www.adlnet.org/xsd/adlseq_v1p2 adlseq_v1p2.xsd 
        http://www.adlnet.org/xsd/adlnav_v1p2 adlnav_v1p2.xsd">
    <metadata>
        <schema>ADL SCORM</schema>
        <schemaversion>2004 4th Edition</schemaversion>
    </metadata>
    <organizations default="org1">
        <organization identifier="org1" adlseq:preventAll="false">
            <title>{escape_xml(course_title)}</title>
            <description>{escape_xml(course_desc)}</description>
            <item identifier="item1" identifierref="res1" isvisible="true">
                <title>{escape_xml(course_title)}</title>
            </item>
        </organization>
    </organizations>
    <resources>
        <resource identifier="res1" type="webcontent" href="content/index.html" adlcp:scormType="sco">
            <file href="content/index.html"/>
        </resource>
    </resources>
</manifest>"""
    else:  # SCORM 1.2
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="{escape_xml(course_id)}" version="{escape_xml(version)}"
    xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
    xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_v1p3.xsd"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1 http://www.imsglobal.org/xsd/imscp_v1p1.xsd
        http://www.adlnet.org/xsd/adlcp_v1p3.xsd http://www.adlnet.org/xsd/adlcp_v1p3.xsd">
    <metadata>
        <schema>ADL SCORM</schema>
        <schemaversion>1.2</schemaversion>
    </metadata>
    <organizations default="org1">
        <organization identifier="org1">
            <title>{escape_xml(course_title)}</title>
            <description>{escape_xml(course_desc)}</description>
            <item identifier="item1" identifierref="res1" isvisible="true">
                <title>{escape_xml(course_title)}</title>
            </item>
        </organization>
    </organizations>
    <resources>
        <resource identifier="res1" type="webcontent" href="content/index.html" adlcp:scormType="sco">
            <file href="content/index.html"/>
        </resource>
    </resources>
</manifest>"""

def create_metadata(course_title, course_desc, author):
    """Create metadata.xml"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<metadata xmlns="http://ltsc.ieee.org/xsd/LOM">
    <general>
        <title>
            <langstring xml:lang="vi">{escape_xml(course_title)}</langstring>
        </title>
        <description>
            <langstring xml:lang="vi">{escape_xml(course_desc)}</langstring>
        </description>
    </general>
    <lifeCycle>
        <contribute>
            <role>creator</role>
            <entity>BEGIN:VCARD FN:{escape_xml(author)} END:VCARD</entity>
        </contribute>
    </lifeCycle>
    <technical>
        <format>text/html</format>
        <location>content/index.html</location>
    </technical>
</metadata>"""

def create_scorm_package(html_file, output_file, course_id, course_title, course_desc="", 
                         author="", course_version="1.0", scorm_version="1.2", max_score=100):
    """Create SCORM package"""
    
    print(f"📖 Đang đọc file HTML: {html_file}")
    html_content = read_html_file(html_file)
    
    if not html_content:
        return False
    
    print(f"🔄 Đang tạo wrapper SCORM {scorm_version}...")
    wrapped_html = create_scorm_wrapper(html_content, scorm_version)
    
    print(f"📝 Đang tạo manifest...")
    manifest = create_manifest(course_id, course_title, course_desc, course_version, scorm_version, max_score)
    
    print(f"📋 Đang tạo metadata...")
    metadata = create_metadata(course_title, course_desc, author or "Anonymous")
    
    print(f"📦 Đang tạo gói ZIP...")
    try:
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add manifest
            zf.writestr('imsmanifest.xml', manifest)
            
            # Add metadata
            zf.writestr('metadata.xml', metadata)
            
            # Add HTML content
            zf.writestr('content/index.html', wrapped_html)
            
            # Add package info
            package_info = {
                "name": course_title,
                "version": course_version,
                "description": course_desc,
                "author": author or "Anonymous",
                "scorm_version": scorm_version,
                "created": datetime.now().isoformat(),
                "moodle_compatible": True,
                "max_score": max_score
            }
            zf.writestr('package.json', json.dumps(package_info, ensure_ascii=False, indent=2))
            
            # Add README
            readme = f"""# {course_title}

## Thông Tin
- Phiên bản: {course_version}
- Tác giả: {author or "Anonymous"}
- Định dạng: SCORM {scorm_version}
- Tạo lúc: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Cách Sử Dụng Trên Moodle

1. Đăng nhập Moodle với tư cách Giáo Viên
2. Vào khóa học → Bật chỉnh sửa
3. Click "Thêm hoạt động" → Chọn "SCORM package"
4. Upload file này
5. Điều chỉnh cài đặt nếu cần
6. Click "Lưu"

## Yêu Cầu

- Moodle 3.8 trở lên
- JavaScript được bật
- Plugin SCORM được bật (yêu cầu liên hệ quản trị viên)

## Hỗ Trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra JavaScript có được bật
2. Liên hệ quản trị viên Moodle
3. Xem nhật ký lỗi trình duyệt (F12)

---
Được tạo bởi HTML to SCORM Converter
"""
            zf.writestr('README.txt', readme)
        
        file_size = os.path.getsize(output_file) / 1024
        print(f"✅ Tạo thành công: {output_file} ({file_size:.1f} KB)")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi tạo gói: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Chuyển đổi file HTML sang SCORM 1.2/2004 cho Moodle',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  python html_to_scorm_cli.py input.html -o output.zip -t "My Course"
  python html_to_scorm_cli.py lesson.html -i course001 -t "Lesson 1" -d "Description"
  python html_to_scorm_cli.py content.html -o package.zip --scorm 2004 --author "Dr. Smith"
        """
    )
    
    parser.add_argument('input', help='File HTML đầu vào')
    parser.add_argument('-o', '--output', help='File ZIP đầu ra (mặc định: input_name.zip)')
    parser.add_argument('-t', '--title', required=True, help='Tiêu đề khóa học')
    parser.add_argument('-i', '--id', help='Mã khóa học (mặc định: random)')
    parser.add_argument('-d', '--description', default='', help='Mô tả khóa học')
    parser.add_argument('-a', '--author', default='', help='Tác giả')
    parser.add_argument('-v', '--version', default='1.0', help='Phiên bản (mặc định: 1.0)')
    parser.add_argument('--scorm', choices=['1.2', '2004'], default='1.2', help='Phiên bản SCORM')
    parser.add_argument('--score', type=int, default=100, help='Điểm tối đa')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"❌ File không tồn tại: {args.input}")
        sys.exit(1)
    
    # Generate output filename
    output_file = args.output or Path(args.input).stem + '.zip'
    
    # Generate course ID if not provided
    course_id = args.id or f"course_{uuid.uuid4().hex[:8]}"
    
    print("🚀 HTML to SCORM Converter - CLI Tool")
    print("=" * 50)
    print(f"📥 Input:         {args.input}")
    print(f"📤 Output:        {output_file}")
    print(f"📚 Tiêu đề:       {args.title}")
    print(f"🆔 Mã khóa:       {course_id}")
    print(f"🏷️  Phiên bản:      {args.version}")
    print(f"📋 SCORM:         {args.scorm}")
    print(f"⭐ Điểm tối đa:    {args.score}")
    print("=" * 50)
    
    success = create_scorm_package(
        html_file=args.input,
        output_file=output_file,
        course_id=course_id,
        course_title=args.title,
        course_desc=args.description,
        author=args.author,
        course_version=args.version,
        scorm_version=args.scorm,
        max_score=args.score
    )
    
    if success:
        print("\n✨ Hoàn tất!")
        print(f"📦 Bạn có thể bây giờ upload {output_file} lên Moodle")
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
