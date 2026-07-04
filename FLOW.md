# Flow hoạt động của upload-toni

Tài liệu này mô tả luồng hiện tại của tool `upload-toni`: từ lúc người dùng chọn folder ảnh, template, mapping, update file cho tới khi xuất file Walmart upload-ready.

## 1. Mục đích tổng quan

Tool này là app desktop Tkinter dùng để tự động hóa flow upload sản phẩm POD lên Walmart.

Luồng chính:

```text
Ảnh gốc + SKU Prefix + Getlinks Template + Update File + Mapping Config
-> đổi tên ảnh
-> upload ảnh lên Cloudinary
-> tạo getlinks output có URL ảnh
-> map dữ liệu vào Walmart Seller Template
-> xuất final Walmart XLSX
```

Code chính nằm trong:

```text
upload_toni.py
```

File cấu hình Cloudinary nằm trong:

```text
.env
```

Tool chỉ kiểm tra sự tồn tại của các biến:

```text
CLOUD_NAME
API_KEY
API_SECRET
```

Không nên ghi giá trị thật của các key này vào tài liệu hoặc log.

## 2. Các input người dùng chọn trong giao diện

Khi mở tool, giao diện yêu cầu các input sau:

| Input | Ý nghĩa |
| --- | --- |
| Folder ảnh gốc | Nơi chứa mockup, swatch, instruction image |
| Đổi tên file trước khi upload | Nếu bật, tool copy và đổi tên ảnh sang chuẩn SKU/image code |
| SKU Prefix | Prefix sản phẩm, ví dụ `120526TA1UGNT1` |
| Getlinks/Image Template | File Excel chứa COLOR, SIZE, SKUWA, Main/Add/Swatch image code |
| Walmart Seller Template | Template gốc tải từ Walmart |
| Mapping Config | File Excel quy định cột Walmart lấy dữ liệu từ đâu |
| Update File | File dữ liệu bổ sung như title, price, description, feature, variant group |
| Cloudinary Batch Name | Folder batch khi upload ảnh lên Cloudinary |
| Output Folder | Nơi lưu file kết quả và log |

## 3. Validate trước khi chạy

Khi bấm `Preview` hoặc `Run All`, tool kiểm tra:

1. Folder ảnh tồn tại.
2. SKU Prefix không được rỗng.
3. Getlinks template tồn tại.
4. Walmart template tồn tại.
5. Mapping config tồn tại.
6. Update file nếu có chọn thì phải tồn tại.
7. Cloudinary batch name không được rỗng.
8. Output folder không được rỗng.
9. File `.env` tồn tại trong cùng folder với app hoặc file exe.

Nếu thiếu một input, tool dừng và báo lỗi.

## 4. Preview hoạt động như thế nào

Nút `Preview` không upload ảnh và không tạo file final.

Preview chỉ:

1. Đọc getlinks template.
2. Chuẩn hóa tên cột theo alias.
3. Đọc mapping config.
4. Log số dòng getlinks.
5. Log số dòng mapping đang enabled.
6. Với 10 dòng đầu, tool thử build:
   - `SKU`
   - `SKUWA`
   - COLOR/SIZE tương ứng

Mục đích là kiểm tra nhanh SKU Prefix và rule màu/size trước khi chạy thật.

## 5. Run All: luồng chạy chính

Khi bấm `Run All`, tool chạy trong background thread theo 3 bước lớn:

```text
Step 1: Rename images
Step 2: Upload images and generate getlinks data
Step 3: Fill Walmart XLSX template
```

## 6. Step 1: Rename images

Hàm chính:

```text
rename_images()
```

Nếu checkbox `Đổi tên file trước khi upload` đang bật, tool tạo folder:

```text
<output_folder>/renamed_images
```

Sau đó tool đọc từng file ảnh trong folder gốc.

Các extension được hỗ trợ:

```text
.png
.jpg
.jpeg
.webp
```

### 6.1. Nếu file đã là full image code

Tool coi file là full image code nếu tên file có:

```text
UGNT hoặc UNGT
```

và có một trong các cụm:

```text
MK
IN
SW
```

Trường hợp này tool chỉ copy file sang `renamed_images`, không đổi logic tên.

### 6.2. Rule nhận diện màu từ tên file

Nếu file chưa phải full image code, tool cố nhận diện màu từ tên file.

Mapping hiện tại:

| Tên màu trong file | Image color code |
| --- | --- |
| Black | `1` |
| Navy | `2` |
| Grey, Gray, Sport Grey, Sport Gray | `3` |
| Green, Military Green | `4` |

Ví dụ:

```text
MK3-BLACK.jpg -> MK3-1.jpg
MK3-NAVY.jpg -> MK3-2.jpg
MK3-GREY.jpg -> MK3-3.jpg
MK3-Military Green.jpg -> MK3-4.jpg
```

### 6.3. Rule đổi SKU theo màu

Tool đang có rule riêng cho T-shirt:

| Màu | SKU dùng để build ảnh/SKUWA |
| --- | --- |
| Black | SKU Prefix gốc |
| Navy | SKU Prefix gốc |
| Grey/Sport Grey | đổi `UGNT1/UNGT1` thành `UGNT4/UNGT4` |
| Green/Military Green | đổi `UGNT1/UNGT1` thành `UGNT3/UNGT3` |

Ví dụ nếu SKU Prefix là:

```text
120526TA1UGNT1
```

thì:

```text
Black -> 120526TA1UGNT1
Navy -> 120526TA1UGNT1
Grey -> 120526TA1UGNT4
Green -> 120526TA1UGNT3
```

### 6.4. File common asset

Nếu file không nhận diện được màu, tool coi đó là common asset.

Ví dụ:

```text
collection.jpg
main-instruction.png
add-instruction.png
```

Với common asset, tool copy file ra nhiều SKU variant:

```text
SKU gốc
SKU variant 4
SKU variant 3
```

Mục đích là để cùng một ảnh instruction/collection có thể dùng cho nhiều SKU variant.

### 6.5. Output của Step 1

Sau khi rename, tool tạo:

```text
<output_folder>/renamed_images/
<output_folder>/renamed_images/rename_log_<timestamp>.csv
```

Log gồm:

| Cột | Ý nghĩa |
| --- | --- |
| Old File | Tên file gốc |
| New File | Tên file sau khi copy/rename |
| Status | Copied, Renamed, Skipped |
| Note | Ghi chú |

Nếu không bật rename, Step 1 bị skip và Step 2 dùng trực tiếp folder ảnh gốc.

## 7. Step 2: Upload ảnh và tạo getlinks output

Hàm chính:

```text
process_getlinks_template()
```

Tool làm các việc sau:

1. Load config Cloudinary từ `.env`.
2. Đọc getlinks template bằng pandas.
3. Chuẩn hóa tên cột theo alias.
4. Kiểm tra bắt buộc có cột `COLOR` và `SIZE`.
5. Nếu thiếu `SKU` hoặc `SKUWA`, tool tự tạo cột.
6. Build lại `SKU` và `SKUWA` cho từng dòng.
7. Build full image code cho các cột ảnh.
8. Tìm file ảnh tương ứng trong folder ảnh.
9. Upload ảnh lên Cloudinary.
10. Ghi URL vào cột URL tương ứng.
11. Xuất getlinks CSV và upload log CSV.

### 7.1. Các cột getlinks được hỗ trợ

Tool có alias để chuẩn hóa tên cột.

Ví dụ các tên sau có thể được hiểu là cùng một cột:

| Chuẩn | Alias được nhận |
| --- | --- |
| `Main_URL` | `Main_URL`, `Main Image_URL`, `Main Image URL`, `Main URL` |
| `Add1` | `Add1`, `Add 1` |
| `Add1_URL` | `Add1_URL`, `Add1 URL (+)`, `Add 1 URL (+)`, `Additional Image URL (+)` |
| `Swatch_URL` | `Swatch_URL`, `Swatch URL`, `SWATCH URL`, `swatch URL` |

Các cặp image column hiện tại:

```text
Main -> Main_URL
Add1 -> Add1_URL
Add2 -> Add2_URL
Add3 -> Add3_URL
Add4 -> Add4_URL
Add5 -> Add5_URL
Swatch -> Swatch_URL
```

### 7.2. Build SKU

Với mỗi dòng getlinks:

1. Nếu dòng có cột `SKU`, ưu tiên dùng `SKU`.
2. Nếu không có, nếu dòng có `PREFIX`, dùng `PREFIX`.
3. Nếu không có, dùng SKU Prefix nhập trên giao diện.
4. Sau đó apply rule màu:
   - Black/Navy giữ SKU.
   - Grey đổi sang variant 4.
   - Green đổi sang variant 3.

### 7.3. Build SKUWA

Tool build SKUWA theo thứ tự ưu tiên:

1. Nếu `SKUWA` đã là full code có `UGNT/UNGT`, giữ nguyên.
2. Nếu `SKUWA` là suffix như `B00S`, ghép với SKU đã adjust theo màu.
3. Nếu `SKUWA` trống, tool tự tạo suffix từ COLOR + SIZE.
4. Nếu không build được suffix, dùng SKU làm fallback.

Mapping màu sang SKUWA letter:

| Màu | SKUWA letter |
| --- | --- |
| Black | `B` |
| Navy | `N` |
| Grey/Sport Grey | `H` |
| Green/Military Green | `F` |

Mapping size:

| Size | Code |
| --- | --- |
| S | `00S` |
| M | `00M` |
| L | `00L` |
| XL | `0XL` |
| 2XL | `2XL` |
| 3XL | `3XL` |
| 4XL | `4XL` |
| 5XL | `5XL` |

Ví dụ:

```text
COLOR = Black, SIZE = S -> B00S
COLOR = Navy, SIZE = XL -> N0XL
COLOR = Grey, SIZE = M -> H00M
COLOR = Green, SIZE = 2XL -> F2XL
```

Sau đó ghép với SKU đã adjust.

### 7.4. Build full image code

Nếu image code trong getlinks đã là full code, tool giữ nguyên.

Nếu chỉ là short code, tool ghép:

```text
adjusted SKU + short image code
```

Ví dụ:

```text
SKU Prefix = 120526TA1UGNT1
COLOR = Black
Main = MK3-1

Full image code = 120526TA1UGNT1MK3-1
```

Với Grey:

```text
SKU Prefix = 120526TA1UGNT1
COLOR = Grey
Main = MK3-3

Full image code = 120526TA1UGNT4MK3-3
```

### 7.5. Tìm ảnh trong folder

Tool tìm file theo full image code và thử các extension:

```text
.png
.jpg
.jpeg
.webp
```

Ví dụ cần tìm:

```text
120526TA1UGNT1MK3-1
```

Tool sẽ thử:

```text
120526TA1UGNT1MK3-1.png
120526TA1UGNT1MK3-1.jpg
120526TA1UGNT1MK3-1.jpeg
120526TA1UGNT1MK3-1.webp
```

### 7.6. Upload Cloudinary

Mỗi ảnh được upload với:

```text
folder = Cloudinary Batch Name
public_id = tên file không có extension
overwrite = True
resource_type = image
```

Tool có cache trong một lần chạy. Nếu cùng một full image code xuất hiện nhiều lần, tool không upload lại mà dùng URL đã upload trước đó.

### 7.7. Output của Step 2

Tool tạo:

```text
<output_folder>/getlinks_output_<timestamp>.csv
<output_folder>/upload_log_<timestamp>.csv
```

Upload log gồm:

| Cột | Ý nghĩa |
| --- | --- |
| Template Column | Cột ảnh nguồn, ví dụ Main/Add1/Swatch |
| URL Column | Cột URL cần ghi |
| Short Code | Code ban đầu trong template |
| Full Image Code | Code đầy đủ sau khi ghép SKU |
| File Name | File ảnh tìm thấy |
| Status | Uploaded, Reused, Missing, Error |
| URL | Cloudinary secure URL |
| Note | Ghi chú lỗi hoặc OK |

## 8. Step 3: Fill Walmart XLSX template

Hàm chính:

```text
generate_walmart_xlsx_from_getlinks_df()
```

Tool làm các việc:

1. Đọc mapping config.
2. Nếu có update file, đọc update file.
3. Chuẩn hóa update file và build full SKUWA.
4. Lấy seller sheet và header row từ mapping.
5. Copy Walmart seller template thành file output mới.
6. Mở file output bằng openpyxl.
7. Xóa dữ liệu cũ ở vùng data.
8. Với mỗi dòng getlinks, tìm update row match theo SKUWA.
9. Với mỗi dòng mapping enabled, resolve giá trị.
10. Ghi giá trị vào cột Excel tương ứng.
11. Save output XLSX.
12. Xuất mapper log CSV.

### 8.1. Mapping config

Mapping file cần có sheet tên:

```text
Mapping
```

Các cột bắt buộc:

| Cột | Ý nghĩa |
| --- | --- |
| Enabled | Có dùng dòng mapping này không |
| Seller Sheet | Sheet trong Walmart template |
| Seller Header Row | Dòng header trong Walmart template |
| Seller Excel Col | Cột Excel cần ghi, ví dụ D, E, F |
| Seller Column | Tên cột seller để log/dễ đọc |
| Source Type | Kiểu nguồn dữ liệu |
| Source Value | Tên cột nguồn |
| Fixed Value | Giá trị cố định nếu Source Type là fixed |

Trong file mẫu hiện tại:

```text
Seller Sheet = Product Content And Site Exp
Seller Header Row = 4
Data Start Row = 7
```

Vì tool ghi data từ:

```text
header_row + 3
```

### 8.2. Các Source Type hiện tại

| Source Type | Ý nghĩa |
| --- | --- |
| `getlinks` | Lấy value từ getlinks output |
| `update_file` | Lấy value từ update file, match theo SKUWA |
| `fixed` | Điền cùng một giá trị cố định cho mọi dòng |
| `blank` | Ép cell rỗng |
| `skip` | Bỏ qua cột này, không ghi |

### 8.3. Match update file

Nếu có update file:

1. Tool chuẩn hóa tên cột update file.
2. Nếu thiếu `SKUWA`, tool tạo cột `SKUWA`.
3. Nếu thiếu `SKU`, tool tạo cột `SKU`.
4. Với mỗi dòng update file, tool build full `SKU` và `SKUWA`.
5. Khi fill Walmart, mỗi dòng getlinks sẽ tìm dòng update file có `SKUWA` giống hệt.

Nếu không tìm thấy:

```text
update_file source -> warning: No matching update row
```

Nếu update file chỉ có một dòng, tool dùng dòng đó làm fallback.

### 8.4. Resolve value theo mapping

Với mỗi dòng mapping:

```text
Source Type = getlinks
Source Value = Main_URL
```

Tool lấy:

```text
getlinks_row["Main_URL"]
```

Với:

```text
Source Type = update_file
Source Value = Product Name
```

Tool lấy:

```text
matched_update_row["Product Name"]
```

Với:

```text
Source Type = fixed
Fixed Value = T-Shirts
```

Tool ghi:

```text
T-Shirts
```

### 8.5. Format ngày

Một số cột ngày được format đặc biệt:

| Cột | Ý nghĩa | Format |
| --- | --- | --- |
| DR | Site Start Date | `YYYY-MM-DD HH:MM:SS` |
| DS | Site End Date | `YYYY-MM-DD` |

Tool set number format là text cho các cột này để tránh Excel tự đổi ngày.

### 8.6. Output của Step 3

Tool tạo:

```text
<output_folder>/final_walmart_upload_ready_<timestamp>.xlsx
<output_folder>/mapper_log_<timestamp>.csv
```

Mapper log gồm:

| Cột | Ý nghĩa |
| --- | --- |
| Excel Row | Dòng Excel output |
| SKUWA | SKUWA của dòng đang fill |
| Seller Column | Cột seller |
| Source Type | Kiểu nguồn |
| Source Value | Cột nguồn |
| Status | OK, Warning, Error, Skipped |
| Note | Ghi chú lỗi/cảnh báo |

## 9. Vai trò các file Excel mẫu

### 9.1. `templates/tshirt1_template.xlsx` tới `tshirt4_template.xlsx`

Đây là getlinks/image template cho T-shirt.

Các file này có cùng cấu trúc nhưng khác thứ tự mockup chính/phụ.

Header chính:

```text
SKU
COLOR
SIZE
SKUWA
Main
Main Image_URL
Add 1
Add1 URL (+)
Add 2
Add2 URL (+)
Add 3
Add3 URL (+)
Add 4
Add4 URL (+)
Add 5
Add5 URL (+)
Swatch
Swatch URL
```

Tool đọc các cột ảnh, build full image code, upload và ghi URL.

### 9.2. `sample-files/Tshirt_mapping_config.xlsx`

Đây là file mapping chính để map dữ liệu vào Walmart template.

Trong file mẫu hiện tại có các sheet:

```text
Mapping
Getlinks Columns
Instructions
Seller Columns
Update File Template
```

Tool chỉ bắt buộc đọc sheet `Mapping`. Các sheet còn lại là tham khảo/hướng dẫn.

### 9.3. `sample-files/Tshirt_update_file_template test.xlsx`

Đây là file bổ sung dữ liệu sản phẩm.

Ví dụ:

```text
Product Name
Selling Price
Site Description
Key Features (+)
Color
Color Category (+)
Swatch Image URL
Site Start Date
Site End Date
Variant Group ID
```

Tool match update file với getlinks output bằng `SKUWA`.

### 9.4. `sample-files/Tshirt-walmart-template.xlsx`

Đây là Walmart seller template.

Sheet đang được mapping hiện tại dùng:

```text
Product Content And Site Exp
```

Header row:

```text
4
```

Data được ghi từ dòng:

```text
7
```

## 10. Những phần đang config được bằng Excel

Các phần sau có thể đổi bằng mapping config mà không cần sửa code, miễn là cấu trúc nguồn vẫn giống:

1. Bật/tắt một cột mapping bằng `Enabled`.
2. Đổi cột Walmart cần ghi bằng `Seller Excel Col`.
3. Đổi sheet output bằng `Seller Sheet`.
4. Đổi header row bằng `Seller Header Row`.
5. Đổi source type giữa `getlinks`, `update_file`, `fixed`, `blank`, `skip`.
6. Đổi fixed value như brand, product type, country, quantity.
7. Đổi cột lấy từ update file.
8. Đổi cột lấy từ getlinks output.

Ví dụ đổi `Spec Product Type` từ:

```text
T-Shirts
```

sang:

```text
Sweatshirts
```

có thể làm trong mapping config nếu Walmart template vẫn dùng cùng cột và cùng rule.

## 11. Những phần đang hard-code trong Python

Các phần sau hiện đang nằm trong code, chưa config được bằng Excel:

1. Danh sách màu hỗ trợ.
2. Cách map màu sang SKU variant.
3. Cách map màu sang SKUWA letter.
4. Danh sách size và size code.
5. Cách nhận diện màu từ tên file ảnh.
6. Cách đổi tên ảnh theo `MK`, `IN`, `SW`.
7. Danh sách image columns cố định: Main, Add1-Add5, Swatch.
8. Cách build full image code.
9. Cách match update file chỉ bằng SKUWA.
10. Source type chỉ hỗ trợ `getlinks`, `update_file`, `fixed`, `blank`, `skip`.
11. Output đang thiên về Walmart seller template.

Vì vậy tool hiện tại rất hợp với T-shirt/Walmart flow, nhưng nếu thêm product type khác quá khác T-shirt thì nên tách rule ra config riêng.

## 12. Khả năng mở rộng thêm product type

### 12.1. Dễ mở rộng

Dễ thêm nếu product mới vẫn giống T-shirt về:

1. Có COLOR.
2. Có SIZE.
3. Có SKUWA suffix.
4. Ảnh đặt theo pattern gần giống `MK...`, `In...`, `sw...`.
5. Walmart template vẫn dùng sheet/cột tương tự.

Ví dụ có thể mở rộng tương đối nhanh:

```text
Hoodie
Sweatshirt
Long Sleeve Shirt
Tank Top
```

### 12.2. Khó mở rộng nếu giữ code hiện tại

Sẽ khó nếu product:

1. Không có size.
2. Không có color.
3. Có variant khác như capacity, material, shape.
4. Có nhiều marketplace khác Walmart.
5. Có naming ảnh khác hẳn.
6. Cần nhiều swatch hoặc nhiều nhóm variant.

Ví dụ:

```text
Mug
Poster
Canvas
Blanket
Ornament
Phone Case
```

Với các loại này, nên refactor sang product profile.

## 13. Hướng nâng cấp mapping thông minh hơn

Hiện tại mapping chỉ copy giá trị đơn giản. Có thể nâng cấp thêm các source type sau:

| Source Type mới | Ý nghĩa |
| --- | --- |
| `template` | Fill text theo mẫu, ví dụ `{Product Name} - {Color} - {Size}` |
| `concat` | Ghép nhiều cột lại |
| `lookup` | Tra bảng config, ví dụ color -> color category |
| `condition` | Nếu điều kiện đúng thì fill value A, ngược lại value B |
| `coalesce` | Lấy update file trước, nếu trống thì dùng fixed fallback |
| `formula` | Tính toán đơn giản như price, weight, package dimension |
| `auto_image` | Tự chọn image URL theo role ảnh |
| `computed` | Gọi hàm built-in như build title, normalize color |

Ví dụ mapping thông minh:

```text
Seller Column: Product Name
Source Type: template
Source Value: {Base Title} - {Color} - {Size}
```

Hoặc:

```text
Seller Column: Color Category (+)
Source Type: lookup
Source Value: COLOR
Lookup Table: Black->Black, Navy->Blue, Grey->Gray, Green->Green
```

## 14. Hướng refactor đề xuất

Để tool dễ mở rộng hơn, nên tách thành 3 lớp:

### 14.1. Product Profile

Mỗi product type có một file config riêng:

```text
profiles/tshirt.yaml
profiles/hoodie.yaml
profiles/mug.yaml
```

Profile chứa:

```text
colors
sizes
sku_variant_rules
skuwa_rules
image_naming_rules
image_columns
default_mapping_file
default_getlinks_template
```

### 14.2. Mapping Engine

Tách logic mapping khỏi GUI.

Mapping engine nên nhận:

```text
getlinks_df
update_df
mapping_config
product_profile
```

và trả về:

```text
filled workbook
mapper log
validation errors
```

### 14.3. Validation Engine

Trước khi upload thật, tool nên validate:

1. Thiếu ảnh nào.
2. SKUWA nào duplicate.
3. SKUWA nào không match update file.
4. Mapping nào trỏ tới cột không tồn tại.
5. Seller Excel Col nào sai.
6. Fixed value nào có vẻ không hợp lệ.
7. Số dòng output có khớp số variant không.

Nếu có lỗi lớn, tool nên báo trước khi upload để tránh tốn thời gian và Cloudinary request.

## 15. Tóm tắt nhanh

Tool hiện tại gồm 3 việc chính:

```text
Rename ảnh -> Upload ảnh/getlinks -> Fill Walmart XLSX
```

Điểm mạnh:

1. Flow gọn.
2. Có mapping config Excel.
3. Có update file match theo SKUWA.
4. Có log cho rename/upload/mapper.
5. Có cache upload trong một lần chạy.

Giới hạn:

1. Product type đang thiên về T-shirt.
2. Rule màu/size/SKUWA/image code đang hard-code.
3. Mapping chưa có logic thông minh như lookup/template/condition.
4. Chưa có validation tổng trước khi upload.

Hướng nâng cấp tốt nhất:

```text
Tách product profile + nâng cấp mapping engine + thêm validation trước upload.
```
