# Bộ công cụ giảng dạy VLUTE

Trang cổng (hub) tập hợp các công cụ giảng dạy chạy trực tiếp trên trình duyệt.
Toàn bộ là web tĩnh — deploy thẳng lên Vercel, không cần build.

## Cấu trúc thư mục

```
vlute-hub/
├── index.html          ← trang cổng (danh sách công cụ)
├── CREATE_LESSON.html   ← Soạn bài giảng → SCORM
├── CREATE_QUIZ.html     ← Tạo ngân hàng câu hỏi E-VLUTE
├── PROCESS_MARK.html    ← Xử lý điểm thành phần
├── vercel.json         ← cấu hình web tĩnh (tùy chọn)
└── README.md
```

## Chạy thử ở máy

Mở trực tiếp `index.html` bằng trình duyệt, hoặc chạy một server tĩnh:

```bash
npx serve .
# hoặc
python3 -m http.server 8080
```

## Deploy lên Vercel

**Cách 1 — kéo–thả (nhanh nhất):** vào https://vercel.com → New Project →
kéo cả thư mục `vlute-hub` vào, hoặc dùng CLI:

```bash
npm i -g vercel
cd vlute-hub
vercel        # xem thử (preview)
vercel --prod # deploy chính thức
```

**Cách 2 — qua GitHub:** đẩy thư mục này lên một repo GitHub → Vercel → Import
repo. Vercel tự nhận đây là static site (không cần Framework, Build Command để trống).

## Thêm một công cụ mới (khoảng 1 phút)

1. Copy file `.html` của công cụ mới vào **cùng thư mục** với `index.html`.
2. Mở `index.html`, tìm mảng `TOOLS` (có chú thích rõ), thêm một khối:

```js
{
  code:"TÊN NGẮN",                 // nhãn mono trên thẻ, vd "SCORM"
  name:"Tên công cụ đầy đủ",
  role:"Mô tả vai trò · 1 dòng",
  desc:"Mô tả ngắn 1–2 câu về công cụ.",
  tags:["Từ khóa 1","Từ khóa 2"],
  file:"TEN_FILE.html",            // đúng tên file vừa copy vào
  accent:"teal",                   // teal | clay | green | amber
  cat:"content",                   // content | assess | grade
  status:"ready",                  // ready = mở được, soon = hiện mờ "sắp có"
  icon:'<path d="..."/>'           // SVG path (stroke), có thể để tạm icon cũ
}
```

3. Lưu lại và deploy lại. Trang tự render thẻ mới, tự đếm số lượng, tự lọc theo
   danh mục và ô tìm kiếm — không phải sửa gì thêm.

### Thêm danh mục mới

Sửa mảng `CATS` ở đầu `<script>` trong `index.html`, rồi dùng `id` danh mục đó
ở trường `cat` của công cụ.

## Ghi chú

- `PROCESS_MARK.html` có tham chiếu ảnh `logo-vlute(960).png`. Nếu muốn hiện logo,
  copy file ảnh đó vào cùng thư mục. Không có ảnh thì công cụ vẫn chạy bình thường.
- Các công cụ lưu nháp bằng bộ nhớ trình duyệt của người dùng; không có dữ liệu
  nào gửi lên máy chủ.
