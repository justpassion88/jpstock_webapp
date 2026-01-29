#!/usr/bin/env python3
_Bc='VNSTOCK_LANGUAGE'
_Bb='VNSTOCK_API_KEY'
_Ba='Dùng Python hệ thống'
_BZ='Solutions:'
_BY='Try reinstalling:'
_BX='❌ INSTALLATION INCOMPLETE'
_BW='Troubleshooting guide:'
_BV='Virtual environment issues'
_BU='Possible causes:'
_BT='Validating installation'
_BS='Installation Complete!'
_BR='VNStock installed successfully!'
_BQ='Thư viện Python #1 Việt Nam về API chứng khoán & phân tích thị trường'
_BP='continue_anyway'
_BO='check_dependencies'
_BN='try_pip_install'
_BM='check_logs'
_BL='module_install_failed'
_BK='install_incomplete_modules'
_BJ='missing_modules'
_BI='continue_without_optional'
_BH='troubleshooting'
_BG='manual_install'
_BF='install_warning'
_BE='install_error'
_BD='missing_optional'
_BC='checking_vnstock'
_BB='colab_manual_then'
_BA='colab_full_mode'
_B9='colab_quick_mode'
_B8='colab_quick_setup_desc'
_B7='colab_quick_setup_title'
_B6='install_dir_exists'
_B5='drive_not_found'
_B4='drive_mount_success'
_B3='unexpected_error'
_B2='cancelled'
_B1='failed_install_deps'
_B0='failed_create_venv'
_A_='installer_not_found'
_Az='select_version'
_Ay='available_versions'
_Ax='documentation'
_Aw='start_using'
_Av='activate_venv'
_Au='quick_start'
_At='installer_failed'
_As='installer_success'
_Ar='browser_auth_fail'
_Aq='browser_auth_start'
_Ap='select_option'
_Ao='manual_entry'
_An='browser_auth'
_Am='choose_auth'
_Al='deps_installed'
_Ak='installing'
_Aj='venv_created'
_Ai='venv_exists'
_Ah='detecting_python'
_Ag='header_title'
_Af='cli_installer.log'
_Ae='vnstock_ezchart>=0.0.2'
_Ad='pta-reload>=1.0.1'
_Ac='pyecharts>=2.0.8'
_Ab='panel>=1.6.1'
_Aa='vnii>=0.1.3'
_AZ='vnai>=2.2.4'
_AY='vnstock>=3.3.0'
_AX='install'
_AW='default'
_AV='/content/drive/MyDrive/.vnstock'
_AU='Dependencies installed'
_AT='solutions'
_AS='consult_guide'
_AR='try_reinstall'
_AQ='venv_issue'
_AP='python_incompatible'
_AO='disk_network_issue'
_AN='install_interrupted'
_AM='possible_causes'
_AL='install_incomplete'
_AK='missing_core'
_AJ='validation_complete'
_AI='checking_core'
_AH='validating'
_AG='colab_manual_cmd'
_AF='colab_setup_steps'
_AE='colab_temp_benefit'
_AD='colab_temp_desc'
_AC='colab_temp_install'
_AB='using_codespaces_python'
_AA='using_colab_python'
_A9='detected_colab'
_A8='cannot_proceed_drive'
_A7='drive_already_mounted'
_A6='drive_mount_step4'
_A5='drive_mount_step3'
_A4='drive_mount_step2'
_A3='drive_mount_step1'
_A2='drive_mount_steps'
_A1='drive_mount_benefit'
_A0='drive_mount_desc'
_z='drive_mount_required'
_y='no_python_found'
_x='enter_number'
_w='complete'
_v='running_installer'
_u='api_key_entered'
_t='using_env_key'
_s='need_install_packages'
_r='all_packages_installed'
_q='installing_deps'
_p='with'
_o='venv_removed_failed'
_n='venv_corrupted'
_m='selecting_python'
_l='found'
_k='step'
_j='header_subtitle'
_i='mac_address'
_h='hardware_uuid'
_g='device_id'
_f='Windows'
_e='.vnstock'
_d='vnstock'
_c='bin'
_b='Scripts'
_a='-m'
_Z='python.exe'
_Y='no_api_key'
_X='enter_api_key'
_W='api_auth'
_V='checking_packages'
_U='packages'
_T='creating_venv'
_S='selected'
_R='requests'
_Q='pip'
_P='nt'
_O='invalid_selection'
_N='full_version'
_M='command'
_L='\n'
_K='vi'
_J='python'
_I='unknown'
_H='display'
_G='version'
_F='INFO'
_E='system'
_D=None
_C=False
_B='path'
_A=True
__version__='3.0.1'
import sys,os,platform,subprocess,shutil,time,argparse,json,hashlib,socket,uuid,requests
from pathlib import Path
from datetime import datetime
REQUIRED_DEPENDENCIES=[_AY,_AZ,_Aa,'numpy>=1.26.4','pandas>=1.5.3','requests>=2.31.0','beautifulsoup4>=4.9.3','aiohttp>=3.11.3','nest-asyncio>=1.6.0','pydantic>=2.0.0','psutil>=5.9.0','pyarrow>=14.0.1','openpyxl>=3.0.0','tqdm>=4.67.0',_Ab,_Ac,_Ad,'duckdb>=1.2.0',_Ae]
COLAB_REQUIREMENTS=[_AY,_AZ,_Aa,_Ad,_Ae,_Ac,_Ab]
CRITICAL_DEPENDENCIES={_R:_R}
HOME_DIR=Path.home()
CONFIG_DIR=HOME_DIR/_e
API_KEY_FILE=CONFIG_DIR/'api_key.json'
USER_INFO_FILE=CONFIG_DIR/'user.json'
LOG_FILE=CONFIG_DIR/_Af
CONFIG_DIR.mkdir(parents=_A,exist_ok=_A)
def save_api_key(api_key:str)->bool:
	try:
		CONFIG_DIR.mkdir(parents=_A,exist_ok=_A);A={'api_key':api_key}
		with open(API_KEY_FILE,'w')as B:json.dump(A,B,indent=2)
		return _A
	except Exception:return _C
def save_user_info(user_info:dict)->bool:
	try:
		CONFIG_DIR.mkdir(parents=_A,exist_ok=_A)
		with open(USER_INFO_FILE,'w')as A:json.dump(user_info,A,indent=2)
		return _A
	except Exception:return _C
def get_username_from_api(api_key:str)->tuple:
	C='Unknown'
	try:
		D={'Authorization':f"Bearer {api_key}"};E='https://vnstocks.com/api/vnstock/user/profile';A=requests.get(E,headers=D,timeout=10)
		if A.status_code==200:B=A.json();F=B.get('username',C);G=B.get('email',_I);return F,G
	except Exception:pass
	return C,_I
def get_hardware_uuid()->str:
	try:
		if platform.system()=='Darwin':
			A=subprocess.run(['system_profiler','SPHardwareDataType'],capture_output=_A,text=_A,timeout=5)
			for B in A.stdout.split(_L):
				if'UUID'in B:return B.split()[-1]
		elif platform.system()=='Linux':
			try:
				with open('/etc/machine-id','r')as C:return C.read().strip()
			except FileNotFoundError:pass
		elif platform.system()==_f:
			try:A=subprocess.run(['wmic','os','get','serialnumber'],capture_output=_A,text=_A,timeout=5);return A.stdout.strip().split(_L)[1]
			except Exception:pass
	except Exception:pass
	return str(uuid.uuid5(uuid.NAMESPACE_DNS,socket.gethostname()))
def get_mac_address()->str:
	try:A=':'.join([f"{uuid.getnode()>>A&255:02x}"for A in range(0,12,2)][::-1]);return A
	except Exception:return _I
def generate_device_id()->dict:
	try:
		from vnai.scope.profile import inspector as D;E=D.fingerprint()
		try:B=get_hardware_uuid();C=get_mac_address()
		except:B=_I;C=_I
		F={'platform':platform.platform(),'machine':platform.machine(),'processor':platform.processor(),_E:platform.system(),'release':platform.release(),'node':platform.node(),'python_version':f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"};return{_g:E,_h:B,_i:C,'system_info':F}
	except ImportError as A:raise ImportError(f"vnai is required for device identification: {A}. Please install it with: pip install vnai")
	except Exception as A:raise RuntimeError(f"Failed to generate device ID: {A}")
def is_virtual_environment()->bool:return hasattr(sys,'real_prefix')or hasattr(sys,'base_prefix')and sys.base_prefix!=sys.prefix
def get_machine_identifier()->str:
	try:return str(uuid.uuid5(uuid.NAMESPACE_DNS,socket.gethostname()))
	except Exception:return str(uuid.uuid4())
def create_user_info(python_executable:str,venv_path:str=_D,device_info:dict=_D,api_key:str=_D)->dict:
	B=api_key;A=device_info
	if A is _D:A=generate_device_id()
	C='vnstock_cli_installer';D=_I
	if B:C,D=get_username_from_api(B)
	E={_G:f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",'executable':python_executable,'is_virtual_env':is_virtual_environment(),'virtual_env_path':venv_path};F={'user':C,'email':D,'uuid':get_machine_identifier(),'os':platform.system(),'os_version':platform.version(),'ip':_I,'cwd':os.getcwd(),_J:E,'time':datetime.now().isoformat(),_g:A[_g],_h:A[_h],_i:A[_i]};return F
class Lang:
	IS_WINDOWS=platform.system()==_f;VI={_Ag:'VNSTOCK - CAI DAT GOI THU VIEN'if IS_WINDOWS else'VNStock - Cài Đặt Gói Thư Viện',_j:'Thu vien Python #1 Viet Nam ve API chung khoan & phan tich thi truong'if IS_WINDOWS else _BQ,_k:'Buoc'if IS_WINDOWS else'Bước',_Ah:'Phat hien cac phien ban Python'if IS_WINDOWS else'Phát hiện các phiên bản Python',_l:'Tim thay'if IS_WINDOWS else'Tìm thấy',_m:'Chon phien ban Python'if IS_WINDOWS else'Chọn phiên bản Python',_S:'Da chon'if IS_WINDOWS else'Đã chọn','using':'Dang su dung'if IS_WINDOWS else'Đang sử dụng',_T:'Tao moi truong ao'if IS_WINDOWS else'Tạo môi trường ảo',_Ai:'Moi truong ao da ton tai'if IS_WINDOWS else'Môi trường ảo đã tồn tại',_Aj:'Moi truong ao da duoc tao'if IS_WINDOWS else'Môi trường ảo đã được tạo',_n:'Moi truong ao bi hong, dang tao lai...'if IS_WINDOWS else'Môi trường ảo bị hỏng, đang tạo lại...',_o:'That bai khi xoa moi truong ao bi hong'if IS_WINDOWS else'Thất bại khi xóa môi trường ảo bị hỏng','creating':'Dang tao'if IS_WINDOWS else'Đang tạo',_p:'voi'if IS_WINDOWS else'với',_q:'Cai dat cac goi phu thuoc'if IS_WINDOWS else'Cài đặt các gói phụ thuộc',_Ak:'Dang cai dat'if IS_WINDOWS else'Đang cài đặt',_U:'goi'if IS_WINDOWS else'gói',_V:'Dang kiem tra cac goi da cai dat...'if IS_WINDOWS else'Đang kiểm tra các gói đã cài đặt...',_r:'Tat ca cac goi da duoc cai dat, bo qua!'if IS_WINDOWS else'Tất cả các gói đã được cài đặt, bỏ qua!',_s:'Can cai dat'if IS_WINDOWS else'Cần cài đặt',_Al:'Cac goi phu thuoc da duoc cai dat'if IS_WINDOWS else'Các gói phụ thuộc đã được cài đặt',_W:'Xac thuc API'if IS_WINDOWS else'Xác thực API',_t:'Dang su dung API key tu bien moi truong'if IS_WINDOWS else'Đang sử dụng API key từ biến môi trường',_Am:'Chon phuong thuc xac thuc:'if IS_WINDOWS else'Chọn phương thức xác thực:',_An:'Xac thuc qua Trinh duyet (OAuth)'if IS_WINDOWS else'Xác thực qua Trình duyệt (OAuth)',_Ao:'Nhap API Key thu cong'if IS_WINDOWS else'Nhập API Key thủ công',_Ap:'Chon (1-2, Enter = 1)'if IS_WINDOWS else'Chọn (1-2, Enter = 1)',_Aq:'Bat dau xac thuc qua trinh duyet...'if IS_WINDOWS else'Bắt đầu xác thực qua trình duyệt...',_Ar:'Xac thuc qua trinh duyet that bai, chuyen sang nhap thu cong'if IS_WINDOWS else'Xác thực qua trình duyệt thất bại, chuyển sang nhập thủ công',_X:'Nhap API key'if IS_WINDOWS else'Nhập API key',_u:'Da nhap API key'if IS_WINDOWS else'Đã nhập API key',_Y:'Chua nhap API key'if IS_WINDOWS else'Chưa nhập API key',_v:'Chay chuong trinh cai dat VNStock'if IS_WINDOWS else'Chạy chương trình cài đặt VNStock','running':'Dang chay'if IS_WINDOWS else'Đang chạy',_As:'VNStock da duoc cai dat thanh cong!'if IS_WINDOWS else'VNStock đã được cài đặt thành công!',_At:'Cai dat that bai voi ma loi'if IS_WINDOWS else'Cài đặt thất bại với mã lỗi',_w:'Hoan tat cai dat!'if IS_WINDOWS else'Hoàn tất cài đặt!',_Au:'Huong dan nhanh:'if IS_WINDOWS else'Hướng dẫn nhanh:',_Av:'Kich hoat moi truong ao:'if IS_WINDOWS else'Kích hoạt môi trường ảo:',_Aw:'Bat dau su dung VNStock:'if IS_WINDOWS else'Bắt đầu sử dụng VNStock:',_Ax:'Tai lieu:'if IS_WINDOWS else'Tài liệu:','log_file':'File log'if IS_WINDOWS else'Xem chi tiết log cài đặt tại',_Ay:'Cac phien ban Python kha dung:'if IS_WINDOWS else'Các phiên bản Python khả dụng:',_Az:'Chon phien ban'if IS_WINDOWS else'Chọn phiên bản',_O:'Lua chon khong hop le'if IS_WINDOWS else'Lựa chọn không hợp lệ',_x:'Vui long nhap so'if IS_WINDOWS else'Vui lòng nhập số',_y:'Khong tim thay Python 3.10-3.14!'if IS_WINDOWS else'Không tìm thấy Python 3.10-3.14!',_A_:'Khong tim thay chuong trinh cai dat'if IS_WINDOWS else'Không tìm thấy chương trình cài đặt',_B0:'That bai khi tao moi truong ao'if IS_WINDOWS else'Thất bại khi tạo môi trường ảo',_B1:'That bai khi cai dat cac goi phu thuoc'if IS_WINDOWS else'Thất bại khi cài đặt các gói phụ thuộc','timeout':'Het thoi gian cho'if IS_WINDOWS else'Hết thời gian chờ',_B2:'Da huy cai dat'if IS_WINDOWS else'Đã hủy cài đặt',_B3:'Loi khong mong doi'if IS_WINDOWS else'Lỗi không mong đợi',_z:'Yeu cau ket noi Google Drive'if IS_WINDOWS else'Yêu cầu kết nối Google Drive',_A0:'Drive can thiet de luu API key.'if IS_WINDOWS else'Drive cần thiết để lưu API key.',_A1:'Ban khong can nhap lai API key sau khi restart!'if IS_WINDOWS else'Bạn không cần nhập lại API key sau khi restart!',_A2:'Vui long ket noi Google Drive:'if IS_WINDOWS else'Vui lòng kết nối Google Drive:',_A3:'1. Nhan bieu tuong thu muc o thanh ben trai'if IS_WINDOWS else'1. Nhấn biểu tượng thư mục ở thanh bên trái',_A4:'2. Nhan nut "Mount Drive"'if IS_WINDOWS else'2. Nhấn nút "Mount Drive"',_A5:'3. Cho phep truy cap trong cua so popup'if IS_WINDOWS else'3. Cho phép truy cập trong cửa sổ popup',_A6:'4. Doi thong bao "Mounted at /content/drive"'if IS_WINDOWS else'4. Đợi thông báo "Mounted at /content/drive"',_A7:'Google Drive da duoc ket noi'if IS_WINDOWS else'Google Drive đã được kết nối',_B4:'Ket noi Google Drive thanh cong!'if IS_WINDOWS else'Kết nối Google Drive thành công!',_B5:'Khong tim thay Google Drive. Vui long ket noi truoc.'if IS_WINDOWS else'Không tìm thấy Google Drive. Vui lòng kết nối trước.',_A8:'Khong the tien hanh ma khong co truy cap Google Drive'if IS_WINDOWS else'Không thể tiến hành mà không có truy cập Google Drive',_A9:'Phat hien moi truong Google Colab'if IS_WINDOWS else'Phát hiện môi trường Google Colab',_AA:'Dang su dung he thong Python cua Google Colab'if IS_WINDOWS else'Đang sử dụng hệ thống Python của Google Colab',_AB:'Dang su dung he thong Python cua GitHub Codespaces'if IS_WINDOWS else'Đang sử dụng hệ thống Python của GitHub Codespaces',_AC:'Cai dat vao session hien tai (tam thoi)'if IS_WINDOWS else'Cài đặt vào session hiện tại (tạm thời)',_AD:'Cac goi se mat sau khi khoi dong lai runtime'if IS_WINDOWS else'Các gói sẽ mất sau khi khởi động lại runtime',_AE:'Cai dat nhanh (~1-2 phut)'if IS_WINDOWS else'Cài đặt nhanh (~1-2 phút)',_B6:'Tho muc cai dat da ton tai'if IS_WINDOWS else'Thư mục cài đặt đã tồn tại',_AF:'Cac buoc cai dat'if IS_WINDOWS else'Các bước cài đặt',_B7:'Cai dat nhanh cho Google Colab'if IS_WINDOWS else'Cài đặt nhanh cho Google Colab',_B8:'Cai dat thu cong de nhanh hon'if IS_WINDOWS else'Cài đặt thủ công để nhanh hơn',_B9:'Dung che do nhanh (khuyen nghi)'if IS_WINDOWS else'Dùng chế độ nhanh (khuyến nghị)',_BA:'Cai dat day du (tu dong)'if IS_WINDOWS else'Cài đặt đầy đủ (tự động)',_AG:'Chay lenh nay trong cell Colab:'if IS_WINDOWS else'Chạy lệnh này trong cell Colab:',_BB:'Sau do chay installer:'if IS_WINDOWS else'Sau đó chạy installer:',_AH:'Dang xac minh cai dat'if IS_WINDOWS else'Đang xác minh cài đặt',_AI:'Kiem tra phu thuoc co ban...'if IS_WINDOWS else'Kiểm tra phụ thuộc cơ bản...',_BC:'Kiem tra cac module VNStock...'if IS_WINDOWS else'Kiểm tra các module VNStock...',_AJ:'Xac minh hoan tat!'if IS_WINDOWS else'Xác minh hoàn tất!',_AK:'Phu thuoc co ban bi thieu'if IS_WINDOWS else'Phụ thuộc cơ bản bị thiếu',_BD:'Goi tuy chon bi thieu'if IS_WINDOWS else'Gói tùy chọn bị thiếu',_BE:'Cai dat that bai'if IS_WINDOWS else'Cài đặt thất bại',_AL:'CAI DAT CHUA HOAN TAT'if IS_WINDOWS else'CÀI ĐẶT CHƯA HOÀN TẤT',_BF:'CAC GOI TACH BIEM BI THIEU'if IS_WINDOWS else'CÁC GÓI TÙYCHỌN BỊ THIẾU',_AM:'Nguyen nhan co the:'if IS_WINDOWS else'Nguyên nhân có thể:',_AN:'Cai dat bi gian doan'if IS_WINDOWS else'Cài đặt bị gián đoạn',_AO:'Trang thai dia hoac mang'if IS_WINDOWS else'Trạng thái đĩa hoặc mạng',_AP:'Phien ban Python khong tuong thich'if IS_WINDOWS else'Phiên bản Python không tương thích',_AQ:'Van de moi truong ao'if IS_WINDOWS else'Vấn đề môi trường ảo',_BG:'Cai dat the cong'if IS_WINDOWS else'Cài đặt thủ công',_BH:'Huong dan khac phuc su co:'if IS_WINDOWS else'Hướng dẫn khắc phục sự cố:',_BI:'Tiep tuc ma khong co cac goi tuy chon?'if IS_WINDOWS else'Tiếp tục mà không có các gói tùy chọn?',_BJ:'Cac module bi thieu:'if IS_WINDOWS else'Các module bị thiếu:',_BK:'CAI DAT THAT BAI'if IS_WINDOWS else'❌ CÀI ĐẶT THẤT BẠI',_BL:'Cac module khong the cai dat'if IS_WINDOWS else'Các module không thể cài đặt từ installer',_BM:'Kiem tra log tai:'if IS_WINDOWS else'Kiểm tra log tại:',_BN:'Thu cai dat bang pip:'if IS_WINDOWS else'Thử cài đặt bằng pip:',_BO:'Kiem tra cac phu thuoc:'if IS_WINDOWS else'Kiểm tra các phụ thuộc:',_AR:'Thu cai dat lai:'if IS_WINDOWS else'Thử cài đặt lại:',_AS:'Xem huong dan:'if IS_WINDOWS else'Xem hướng dẫn:',_AT:'Giai phap:'if IS_WINDOWS else'Giải pháp:',_BP:'Tiep tuc? (y/n): 'if IS_WINDOWS else'Tiếp tục? (y/n): '};EN={_Ag:'VNStock Package Installer',_j:'Vietnam #1 Python Library for Stock API & Analysis',_k:'Step',_Ah:'Detecting Python Versions',_l:'Found',_m:'Selecting Python Version',_S:'Selected','using':'Using',_T:'Creating Virtual Environment',_Ai:'Virtual environment exists',_Aj:'Virtual environment created',_n:'Virtual environment corrupted, recreating...',_o:'Failed to remove corrupted virtual environment','creating':'Creating',_p:_p,_q:'Installing Dependencies',_Ak:'Installing',_U:_U,_V:'Checking installed packages...',_r:'All packages already installed, skipping!',_s:'Need to install',_Al:_AU,_W:'API Authentication',_t:'Using API key from environment',_Am:'Choose authentication method:',_An:'Browser Authentication (OAuth)',_Ao:'Manual API Key Entry',_Ap:'Select (1-2, Enter = 1)',_Aq:'Starting browser authentication...',_Ar:'Browser auth failed, falling back to manual',_X:'Enter API key',_u:'API key entered',_Y:'No API key provided',_v:'Running VNStock Installer','running':'Running',_As:_BR,_At:'Installer failed with code',_w:_BS,_Au:'Quick Start Guide:',_Av:'Activate virtual environment:',_Aw:'Start using VNStock:',_Ax:'Documentation:','log_file':'Log file',_Ay:'Available Python versions:',_Az:'Select version',_O:'Invalid selection',_x:'Please enter a number',_y:'No Python 3.10-3.14 found!',_A_:'Installer not found',_B0:'Failed to create virtual environment',_B1:'Failed to install dependencies','timeout':'Timeout',_B2:'Installation cancelled',_B3:'Unexpected error',_z:'Google Drive Mount Required',_A0:'Drive is needed to store your API key.',_A1:"You won't need to re-enter API key after restart!",_A2:'Please mount Google Drive:',_A3:'1. Click the folder icon in the left sidebar',_A4:'2. Click the "Mount Drive" button',_A5:'3. Authorize access in the popup window',_A6:'4. Wait for "Mounted at /content/drive" message',_A7:'Google Drive already mounted',_B4:'Google Drive mounted successfully!',_B5:'Google Drive not found. Please mount it first.',_A8:'Cannot proceed without Google Drive access',_A9:'Detected Google Colab environment',_AA:"Using Google Colab's system Python",_AB:"Using GitHub Codespaces' system Python",_AC:'Installing to current session (temporary)',_AD:'Packages will be lost after runtime restart',_AE:'Fast installation (~1-2 minutes)',_B6:'Installation directory exists',_B7:'Quick Setup for Google Colab',_B8:'Pre-install packages manually for faster setup',_B9:'Use Quick Setup (recommended for Colab)',_BA:'Full setup (auto-install packages)',_AG:'Run this command in a Colab cell:',_BB:'Then run the installer:',_AF:'Setup Steps',_AH:_BT,_AI:'Checking core dependencies...',_BC:'Checking VNStock modules...',_AJ:'Validation complete!',_AK:'Core dependencies missing',_BD:'Optional packages missing',_BE:'Installation failed',_AL:'INSTALLATION INCOMPLETE',_BF:'OPTIONAL PACKAGES MISSING',_AM:_BU,_AN:'Installation was interrupted',_AO:'Disk space or network issues',_AP:'Incompatible Python version',_AQ:_BV,_BG:'Manual installation',_BH:_BW,_BI:'Continue without optional packages?',_BJ:'Missing vnstock modules:',_BK:_BX,_BL:'Modules failed to install from installer',_BM:'Check logs at:',_BN:'Try pip install:',_BO:'Check dependencies:',_AR:_BY,_AS:_BW,_AT:_BZ,_BP:'Continue anyway? (y/n): '}
	@classmethod
	def get(A,lang=_K):return A.VI if lang==_K else A.EN
class Colors:HEADER='\x1b[95m';OKBLUE='\x1b[94m';OKCYAN='\x1b[96m';OKGREEN='\x1b[92m';WARNING='\x1b[93m';FAIL='\x1b[91m';ENDC='\x1b[0m';BOLD='\x1b[1m';UNDERLINE='\x1b[4m';PURPLE='\x1b[35m';YELLOW='\x1b[33m';CYAN='\x1b[36m';WHITE='\x1b[37m';GREY='\x1b[90m';VNSTOCK_GREEN='\x1b[38;5;71m';VNSTOCK_PURPLE='\x1b[38;5;135m';VNSTOCK_BLUE='\x1b[38;5;33m'
class ASCIIArt:LOGO='\n██╗   ██╗███╗   ██╗███████╗████████╗ ██████╗  ██████╗██╗  ██╗\n██║   ██║████╗  ██║██╔════╝╚══██╔══╝██╔═══██╗██╔════╝██║ ██╔╝\n██║   ██║██╔██╗ ██║███████╗   ██║   ██║   ██║██║     █████╔╝ \n╚██╗ ██╔╝██║╚██╗██║╚════██║   ██║   ██║   ██║██║     ██╔═██╗ \n ╚████╔╝ ██║ ╚████║███████║   ██║   ╚██████╔╝╚██████╗██║  ██╗\n  ╚═══╝  ╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚═════╝  ╚═════╝╚═╝  ╚═╝\n';HEADER_TEMPLATE='\n╔════════════════════════════════════════════════════════════════════════════════════════════════╗\n║{title:^96}║\n║{subtitle:^96}║\n║{version:^96}║\n╚════════════════════════════════════════════════════════════════════════════════════════════════╝\n';DIVIDER_THICK='═'*96;DIVIDER_THIN='─'*96;DIVIDER_DOT='·'*96;SUCCESS='\n    ███████╗██╗   ██╗ ██████╗ ██████╗███████╗███████╗███████╗\n    ██╔════╝██║   ██║██╔════╝██╔════╝██╔════╝██╔════╝██╔════╝\n    ███████╗██║   ██║██║     ██║     █████╗  ███████╗███████╗\n    ╚════██║██║   ██║██║     ██║     ██╔══╝  ╚════██║╚════██║\n    ███████║╚██████╔╝╚██████╗╚██████╗███████╗███████║███████║\n    ╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝╚══════╝╚══════╝╚══════╝\n    ';CHECKMARK='✓';CROSSMARK='✗';ARROW='→';BULLET='•';HOURGLASS='⏳';ROCKET='🚀';PACKAGE='📦';WRENCH='🔧';SPARKLES='✨'
class ProgressBar:
	def __init__(A,total=100,width=50,prefix='Progress:'):A.total=total;A.width=width;A.prefix=prefix;A.current=0
	def update(A,value,suffix=''):B=value;A.current=B;C=int(A.width*B/A.total);D='█'*C+'░'*(A.width-C);E=B/A.total*100;print(f"\r{A.prefix} |{D}| {E:.1f}% {suffix}",end='');sys.stdout.flush()
	def finish(A,message='Complete!'):A.update(A.total,message);print()
class VNStockCLIInstaller:
	def __init__(A,interactive=_A,verbose=_C,language=_K):B=language;A.interactive=interactive;A.verbose=verbose;A.language=B;A.is_vietnamese=B==_K;A.lang=Lang.get(B);A.python_versions=[];A.selected_python=_D;A.venv_path=_D;A.venv_type=_D;A.newly_installed_packages=set();A.packages_before_sponsor=set();A.is_colab=A.detect_google_colab();A.is_codespaces=A.detect_codespaces();A.log_file=Path.home()/_e/_Af;A.log_file.parent.mkdir(parents=_A,exist_ok=_A)
	def detect_google_colab(A):
		try:import google.colab;return _A
		except ImportError:return _C
	def detect_codespaces(A):return os.environ.get('CODESPACES')=='true'or os.environ.get('GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN')is not _D
	def mount_google_drive(A):
		if not A.is_colab:return _A
		B=Path('/content/drive/MyDrive')
		if B.exists():A.print_detail(A.lang[_A7]);C=Path(_AV);C.mkdir(parents=_A,exist_ok=_A);return _A
		D=f"📁 {A.lang[_z]}";print(f"\n{Colors.BOLD}{Colors.VNSTOCK_GREEN}{D}{Colors.ENDC}");print(ASCIIArt.DIVIDER_DOT);print(f"\n{Colors.VNSTOCK_GREEN}{A.lang[_A0]}{Colors.ENDC}");print(f"   {A.lang[_A1]}");print(f"\n{Colors.BOLD}{Colors.VNSTOCK_GREEN}{A.lang[_A2]}{Colors.ENDC}");print(f"  {A.lang[_A3]}");print(f"  {A.lang[_A4]}");print(f"  {A.lang[_A5]}");print(f"  {A.lang[_A6]}");print(f"\n{Colors.BOLD}{Colors.VNSTOCK_GREEN}⚙️ Hoặc chạy lệnh:{Colors.ENDC}");print(f"\n{Colors.YELLOW}from google.colab import drive");print(f"drive.mount('/content/drive'){Colors.ENDC}");print();print(f"\n{Colors.BOLD}{Colors.FAIL}⚠️  Chạy lại installer sau khi mount Drive{Colors.ENDC}");print();return _C
	def print_header(A):B=A.lang[_j];print(Colors.VNSTOCK_GREEN+ASCIIArt.LOGO+Colors.ENDC);print(Colors.VNSTOCK_GREEN+B+Colors.ENDC);print(Colors.VNSTOCK_GREEN+ASCIIArt.DIVIDER_THICK+Colors.ENDC);print()
	def log(A,message,level=_F):
		B=time.strftime('%Y-%m-%d %H:%M:%S')
		with open(A.log_file,'a')as C:C.write(f"[{B}] [{level}] {message}\n")
	def print_step(B,step,total,message_key=_D,message=_D):
		A=message_key;D=f"{B.lang[_k]} {step}/{total}"
		if A:C=B.lang.get(A,A)
		else:C=message or''
		print(f"\n{Colors.BOLD}[{D}] {C}{Colors.ENDC}");print(ASCIIArt.DIVIDER_THIN)
	def print_success(A,message):print(f"{Colors.OKGREEN}{ASCIIArt.CHECKMARK} {message}{Colors.ENDC}")
	def print_error(A,message):print(f"{Colors.FAIL}{ASCIIArt.CROSSMARK} {message}{Colors.ENDC}")
	def print_warning(A,message):print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")
	def print_info(B,message):A=f"{Colors.VNSTOCK_GREEN}{ASCIIArt.BULLET}";print(f"{A} {message}{Colors.ENDC}")
	def print_detail(B,message):A=f"{Colors.VNSTOCK_PURPLE}{ASCIIArt.CHECKMARK}";print(f"{A} {message}{Colors.ENDC}")
	def show_colab_quick_setup(A):
		if not A.is_colab:return _C
		print(f"\n{Colors.BOLD}{A.lang[_AF]}:{Colors.ENDC}");print(ASCIIArt.DIVIDER_DOT);print(f"\n{Colors.CYAN}Option 1: Quick Setup (⚡ Recommended){Colors.ENDC}");print('  ⏱️  Time: ~1 minute | Packages pre-installed');print(f"\n{Colors.CYAN}Option 2: Full Setup (Auto){Colors.ENDC}");print('  ⏱️  Time: ~5-10 minutes | Auto-install all packages')
		if A.interactive:
			print();B=input(f"{Colors.CYAN}Choose setup mode [1]: {Colors.ENDC}").strip()
			if not B or B=='1':return _A
			else:return _C
		else:return _A
	def show_quick_setup_instructions(A):
		print(f"\n{Colors.BOLD}🚀 Manual Setup Instructions:{Colors.ENDC}");print(ASCIIArt.DIVIDER_DOT);print(f"\n{Colors.CYAN}{A.lang[_AG]}{Colors.ENDC}");print(f"\n{Colors.YELLOW}{COLAB_MANUAL_INSTALL}{Colors.ENDC}\n");print(f"{Colors.OKBLUE}Steps:{Colors.ENDC}");print('1. Copy the command above');print('2. Paste it in a Colab cell (press Shift+Enter)');print('3. Wait ~2 minutes for installation to complete');print('4. Then come back and run this installer');print()
		if A.interactive:input(f"{Colors.CYAN}Press Enter when ready to continue...{Colors.ENDC}")
	def animate_loading(E,message='Loading',duration=2):
		A=message;B=['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏'];C=time.time()+duration
		while time.time()<C:
			for D in B:print(f"\r{Colors.CYAN}{D} {A}...{Colors.ENDC}",end='');sys.stdout.flush();time.sleep(.1)
		print(f"\r{Colors.OKGREEN}{ASCIIArt.CHECKMARK} {A}... Done!{Colors.ENDC}")
	def detect_python_versions(A):
		d='Python';c='python3';P='--version';M='.'
		if A.is_colab:
			B=_J;A.print_info(A.lang[_AA])
			try:H=subprocess.run([B,P],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=_A,timeout=2);I=H.stdout.strip();D=I.split()[1];F=D.split(M);E=int(F[0]);C=int(F[1]);A.python_versions=[{_M:[B],_B:[B],_G:f"{E}.{C}",_N:D,_H:B}];return _A
			except Exception as Q:A.print_error(f"Failed to detect Colab Python: {Q}");return _C
		elif A.is_codespaces:
			B=c;A.print_info(A.lang[_AB])
			try:H=subprocess.run([B,P],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=_A,timeout=2);I=H.stdout.strip();D=I.split()[1];F=D.split(M);E=int(F[0]);C=int(F[1]);A.python_versions=[{_M:[B],_B:[B],_G:f"{E}.{C}",_N:D,_H:B}];return _A
			except Exception as Q:A.print_error(f"Failed to detect Codespaces Python: {Q}");return _C
		else:
			K=[];L=set()
			if platform.system()==_f:
				import winreg as G;e=[(G.HKEY_CURRENT_USER,'Software\\Python\\PythonCore'),(G.HKEY_LOCAL_MACHINE,'SOFTWARE\\Python\\PythonCore'),(G.HKEY_CURRENT_USER,'Software\\Python\\ContinuumAnalytics')]
				for(f,g)in e:
					try:
						with G.OpenKey(f,g)as U:
							V=0
							while _A:
								try:
									D=G.EnumKey(U,V);V+=1
									try:R=D.split(M);E=int(R[0]);C=int(R[1])if len(R)>1 else 0
									except(ValueError,IndexError):continue
									if not(E==3 and 10<=C<=14):continue
									try:
										W=G.OpenKey(U,D+'\\InstallPath');X=G.QueryValue(W,'');G.CloseKey(W);S=Path(X)/_Z
										if S.exists():
											J=f"{E}.{C}"
											if J not in L:K.append({_M:[str(S)],_B:[str(S)],_G:J,_N:D,_H:f"python{E}.{C}"});L.add(J);A.print_success(f"{A.lang[_l]}: Python {E}.{C} at {X}")
									except Exception:continue
								except OSError:break
					except Exception:continue
				if not K:
					N=shutil.which('py')
					if N:
						for C in[14,13,12,11,10]:
							try:
								H=subprocess.run([N,f"-3.{C}",P],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=_A,timeout=2)
								if H.returncode==0 and d in H.stdout:
									Y=H.stdout.split()[1];Z=Y.split(M);h=int(Z[0]);O=int(Z[1]);T=f"{h}.{O}"
									if T not in L:K.append({_M:[N,f"-3.{O}"],_B:[N,f"-3.{O}"],_G:T,_N:Y,_H:f"py -3.{O}"});L.add(T)
							except Exception:continue
				a=[]
			else:a=['python3.14','python3.13','python3.12','python3.11','python3.10',c,_J]
			for B in a:
				try:
					b=subprocess.run([B,P],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=_A,timeout=2)
					if b.returncode!=0:continue
					I=b.stdout.strip()
					if not I or d not in I:continue
					try:D=I;F=D.split()[1].split(M);E=int(F[0]);C=int(F[1])
					except(IndexError,ValueError):continue
					if not(E==3 and 10<=C<=14):continue
					J=f"{E}.{C}"
					if J in L:continue
					K.append({_M:[B],_B:[B],_G:J,_N:D.split()[1],_H:B});L.add(J)
				except Exception:continue
			A.python_versions=K
			if not K:A.print_error(A.lang[_y]);return _C
			return _A
	def select_python_version(A):
		A.print_step(2,6,_m)
		if len(A.python_versions)==1:A.selected_python=A.python_versions[0];E=A.selected_python.get(_H,' '.join(A.selected_python[_M]));A.print_detail(f"{A.lang[_S]}: {E} (Python {A.selected_python[_G]})");return _A
		if A.interactive:
			print(f"\n{Colors.BOLD}Các phiên bản Python:{Colors.ENDC}")
			for(F,C)in enumerate(A.python_versions,1):print(f"  {F}. {C[_H]} - Python {C[_N]}")
			while _A:
				try:
					B=input(f"\n{Colors.CYAN}Chọn phiên bản (Enter = 1): {Colors.ENDC}").strip()
					if not B:B='1'
					D=int(B)-1
					if 0<=D<len(A.python_versions):A.selected_python=A.python_versions[D];break
					else:A.print_error(A.lang[_O])
				except ValueError:A.print_error(A.lang[_x])
		else:A.selected_python=A.python_versions[0]
		A.print_detail(f"{A.lang[_S]}: {A.selected_python[_H]} (Python {A.selected_python[_G]})");return _A
	def select_venv_configuration(A):
		D='.venv';A.print_step(3,6,_T)
		if A.is_colab:A.venv_type=_E;A.venv_path=_D;A.print_info(f"🔥 {A.lang[_AC]}");A.print_detail(f"   {A.lang[_AD]}");A.print_detail(f"   ⚡ {A.lang[_AE]}");A.print_detail('   📁 API key sẽ được lưu trong Drive');return _A
		if A.is_codespaces:A.venv_type=_E;A.venv_path=_D;A.print_info('GitHub Codespaces detected - using system Python');return _A
		if not A.interactive:A.venv_type=_AW;A.venv_path=Path.home()/D;return _A
		print(f"\n{Colors.BOLD}{A.lang[_T]}:{Colors.ENDC}");print('  1. Dùng ~/.venv (mặc định)');print('  2. Chỉ định đường dẫn tùy chỉnh');print('  3. Dùng Python hệ thống (không venv)')
		while _A:
			B=input(f"\n{Colors.CYAN}Lựa chọn (1-3, Enter = 1): {Colors.ENDC}").strip()
			if not B:B='1'
			if B=='1':A.venv_type=_AW;A.venv_path=Path.home()/D;A.print_info(f"Dùng: {A.venv_path}");return _A
			elif B=='2':
				C=input(f"{Colors.CYAN}Nhập đường dẫn (~ để home): {Colors.ENDC}").strip()
				if C:A.venv_type='custom';A.venv_path=Path(C).expanduser();A.print_info(f"Dùng: {A.venv_path}");return _A
				else:A.print_error(A.lang[_O])
			elif B=='3':A.venv_type=_E;A.venv_path=_D;A.print_info(_Ba);return _A
			else:A.print_error(A.lang[_O])
	def check_python_version(C):
		A=sys.version_info;B=f"{A.major}.{A.minor}.{A.micro}";print(f"Current Python: {B}")
		if A.major<3 or A.major==3 and A.minor<10:C.print_error(f"Python 3.10+ required (found {B})");return _C
		C.print_success(f"Python {B} is compatible");return _A
	def create_virtual_environment(A):
		if A.venv_type==_E:A.print_success(_Ba);return _A
		if A.venv_path is _D:A.print_error('Venv path not configured');return _C
		if A.venv_path.exists():
			if A._is_venv_healthy():A.print_detail(f"Dùng venv hiện tại: {A.venv_path}");return _A
			else:
				A.print_warning(A.lang[_n])
				try:shutil.rmtree(A.venv_path)
				except Exception as B:A.print_error(f"{A.lang[_o]}: {B}");return _C
		try:C=A.selected_python[_B][0]if isinstance(A.selected_python[_B],list)else A.selected_python[_B];A.print_info(f"Tạo venv: {A.venv_path}");subprocess.run([C,_a,'venv',str(A.venv_path)],check=_A,capture_output=not A.verbose);A.print_detail(f"Venv được tạo: {A.venv_path}");return _A
		except Exception as B:A.print_error(f"Tạo venv thất bại: {B}");return _C
	def _is_venv_healthy(A):
		if not A.venv_path:return _C
		if A.venv_type==_E:return _A
		if os.name==_P:return(A.venv_path/_b/_Z).exists()
		else:return(A.venv_path/_c/_J).exists()
	def get_pip_command(A):
		if A.is_colab:B=A.selected_python[_B][0]if isinstance(A.selected_python[_B],list)else A.selected_python[_B];return f"{B} -m pip"
		elif A.venv_path:
			if os.name==_P:return str(A.venv_path/_b/_Q)
			else:return str(A.venv_path/_c/_Q)
		B=A.selected_python[_B][0]if isinstance(A.selected_python[_B],list)else A.selected_python[_B];return f"{B} -m pip"
	def check_packages_installed(D,package_list=_D):
		I='http';E=package_list;import sys as A,io
		if E is _D:E=REQUIRED_DEPENDENCIES
		F=[]
		for B in E:
			if B and not B.startswith('#'):
				if B.startswith(I):C=B.split('/')[-1].split('-')[0]
				else:C=B.split('>=')[0].split('==')[0].split('<')[0].split('>')[0].split('~')[0].strip()
				if C and not C.startswith(I):F.append(C)
		J=A.path.copy()
		if D.is_colab and D.venv_path:A.path.insert(0,str(D.venv_path))
		G=[]
		for H in F:
			try:
				K=A.stdout;A.stdout=io.StringIO()
				try:__import__(H.replace('-','_'))
				finally:A.stdout=K
			except Exception:G.append(H)
		A.path=J;return G
	def install_dependencies(A):
		N='https://vnstocks.com/api/simple';M='--extra-index-url';A.print_step(4,6,_q);F=set()
		if A.is_colab:F=A._get_installed_packages();A.log(f"Packages before install: {len(F)}",_F)
		if A.is_colab:A.print_info(A.lang[_V]);E=COLAB_REQUIREMENTS;B=A.check_packages_installed(E)
		else:A.print_info(A.lang[_V]);E=REQUIRED_DEPENDENCIES;B=A.check_packages_installed(E)
		if not B:A.print_success(A.lang[_r]);return _A
		G=', '.join(B[:5])
		if len(B)>5:G+='...'
		if A.is_colab:A.print_info(f"Installing missing packages ({len(B)}): {G}")
		else:O=f"{A.lang[_s]} {len(B)} {A.lang[_U]}: {G}";A.print_info(O)
		K=[A for A in E if any(B in A for B in B)or A.startswith('https://')];P=[A for A in K if _d in A.lower()];Q=[A for A in K if _d not in A.lower()];R=P+Q;C=Path('/tmp/vnstock_requirements.txt');C.write_text(_L.join(R));H=A.get_pip_command();D=ProgressBar(total=100,prefix='Installing dependencies')
		try:
			for S in range(0,91,10):D.update(S);time.sleep(.1)
			if A.is_colab:T=A.selected_python[_B][0]if isinstance(A.selected_python[_B],list)else A.selected_python[_B];I=[T,_a,_Q,_AX,'--no-cache-dir',M,N,'-r',str(C)];J=subprocess.run(I,capture_output=_A,text=_A,timeout=600)
			else:
				if isinstance(H,str):L=H.split()
				else:L=list(H)
				I=L+[_AX,M,N,'-r',str(C)];J=subprocess.run(I,capture_output=_A,text=_A,timeout=300)
			D.update(100);D.finish('Installed!');C.unlink(missing_ok=_A)
			if J.returncode!=0:
				A.print_warning('Some packages had warnings')
				if A.verbose:print(J.stderr[:500])
			else:A.print_detail(_AU)
			A.log(_AU,'SUCCESS')
			if A.is_colab:U=A._get_installed_packages();V=U-F;A.log(f"Dependencies installed: {len(V)} packages",_F)
			return _A
		except subprocess.TimeoutExpired:D.finish('Timeout!');C.unlink(missing_ok=_A);A.print_error('Installation timeout (10 minutes)');return _C
		except Exception as W:D.finish('Failed!');C.unlink(missing_ok=_A);A.print_error(f"Failed to install dependencies: {W}");return _C
	def _get_installed_packages(A)->set:
		try:
			C=A.selected_python[_B][0]if isinstance(A.selected_python[_B],list)else A.selected_python[_B];B=subprocess.run([C,_a,_Q,'list','--format=json'],capture_output=_A,text=_A,timeout=30)
			if B.returncode!=0:return set()
			import json;D=json.loads(B.stdout);return{A['name'].lower()for A in D}
		except Exception as E:A.print_warning(f"Could not get package list: {E}");return set()
	def copy_vnstock_packages_to_drive(A):
		K='__pycache__'
		if not A.is_colab:return _A
		if not hasattr(A,'newly_installed_packages'):A.print_warning('No package diff available, skipping backup');return _A
		if not A.newly_installed_packages:A.print_info('No new packages to backup');return _A
		E=Path('/content/drive/MyDrive/.venv');L=A.selected_python[_B][0]if isinstance(A.selected_python[_B],list)else A.selected_python[_B];I=subprocess.run([L,'-c','import site; print(site.getsitepackages()[0])'],capture_output=_A,text=_A,timeout=5)
		if I.returncode!=0:A.print_warning('Could not find site-packages location');return _A
		F=Path(I.stdout.strip())
		if not F.exists():A.print_warning(f"Site-packages not found: {F}");return _A
		E.mkdir(parents=_A,exist_ok=_A);A.print_info(f"📦 Backing up {len(A.newly_installed_packages)} packages...");B=0;J=0
		for D in sorted(A.newly_installed_packages):
			M=[f"{D}",f"{D}-*",f"{D.replace("-","_")}",f"{D.replace("-","_")}-*"];G=[]
			for N in M:G.extend(F.glob(N))
			if not G:J+=1;continue
			for C in G:
				if not C.is_dir()or K in C.name:continue
				H=E/C.name
				try:
					if H.exists():shutil.rmtree(H)
					shutil.copytree(C,H,ignore=shutil.ignore_patterns(K,'*.pyc'));B+=1
					if B%10==0:A.log(f"Copied {B} folders",_F)
				except Exception as O:A.log(f"Failed to copy {C.name}: {O}",'WARNING')
		if B>0:A.print_success(f"Backed up {B} folders to Drive: {E}");A.log(f"Backup complete: {B} copied, {J} skipped",_F);return _A
		else:A.print_warning('No packages copied');return _A
	def install_critical_dependencies(A):
		C=[]
		for(G,H)in CRITICAL_DEPENDENCIES.items():
			try:__import__(H)
			except ImportError:C.append(G)
		if not C:return _A
		D=', '.join(C)
		if A.is_vietnamese:E=f"Đang kiểm tra các gói hệ thống ({D})..."
		else:E=f"Checking system packages ({D})..."
		A.print_info(E)
		try:
			import subprocess as I;J=A.selected_python[_B][0]if isinstance(A.selected_python[_B],list)else A.selected_python[_B]
			for B in C:
				if A.is_vietnamese:A.print_info(f"Đang cài đặt {B}...")
				else:A.print_info(f"Installing {B}...")
				K=I.run([J,_a,_Q,_AX,'--quiet',B],capture_output=_A,timeout=60)
				if K.returncode!=0:
					if A.is_vietnamese:A.print_warning(f"Cảnh báo: Không cài được {B} (sẽ thử tiếp tục)")
					else:A.print_warning(f"Warning: Failed to install {B} (will try to continue)")
				else:A.print_success(f"{B} installed")
			return _A
		except Exception as F:
			if A.is_vietnamese:A.print_warning(f"Lỗi khi cài dependencies: {F}")
			else:A.print_warning(f"Error installing dependencies: {F}")
			return _A
	def get_api_key(A,provided_api_key=_D):
		A.print_step(5,6,_W);B=provided_api_key or os.environ.get(_Bb,'')
		if B:save_api_key(B);A.print_success(A.lang[_t]);return B
		if not A.interactive:A.print_warning(A.lang[_Y]);return
		print(f"\n{Colors.BOLD}{A.lang[_W]}:{Colors.ENDC}");print(ASCIIArt.DIVIDER_DOT);print()
		if A.is_vietnamese:print(f"{Colors.CYAN}Lấy API key từ tài khoản của bạn:{Colors.ENDC}");print('  1. Truy cập: https://vnstocks.com/account');print("  2. Sao chép API key từ phần 'API Key của bạn'");print('  3. Dán vào đây')
		else:print(f"{Colors.CYAN}Get API key from your account:{Colors.ENDC}");print('  1. Visit: https://vnstocks.com/account');print("  2. Copy your API key from 'Your API Key' section");print('  3. Paste it here')
		if A.is_vietnamese:C=f"\n{Colors.CYAN}{A.lang[_X]}: ";C+=f"{Colors.ENDC}"
		else:C=f"\n{Colors.CYAN}{A.lang[_X]}: ";C+=f"{Colors.ENDC}"
		B=input(C).strip()
		if B:
			save_api_key(B);A.print_success(A.lang[_u]);D=generate_device_id();E=create_user_info(python_executable=A.selected_python[_B][0]if isinstance(A.selected_python[_B],list)else A.selected_python[_B],venv_path=str(A.venv_path)if A.venv_path else _D,device_info=D,api_key=B);save_user_info(E)
			if A.is_vietnamese:A.print_info('✓ Đã lưu thông tin cấu hình')
			else:A.print_info('✓ Configuration saved')
			return B
		else:A.print_error(A.lang[_Y]);return
	def validate_installation(A):
		E='pandas';D='numpy';F=_AH;G=A.lang.get(F,_BT);A.print_step(7,7,message=G);H={D:D,E:E,_R:_R,_d:_d};B=[];I=A.lang.get(_AI,'Checking core...');A.print_info(I)
		for(C,J)in H.items():
			if not A._check_package_import(J):B.append(C);A.print_error(f"✗ {C}")
			else:A.print_success(f"✓ {C}")
		if B:return A._show_core_error(B)
		else:K=A.lang.get(_AJ,'✓ Installation successful!');A.print_success(K);return _A
	def _check_package_import(A,import_name:str)->bool:
		try:
			if A.is_colab or A.is_codespaces:B=A.selected_python[_B][0]if isinstance(A.selected_python[_B],list)else A.selected_python[_B]
			elif A.venv_path and A.venv_type!=_E:
				if os.name==_P:B=str(A.venv_path/_b/_Z)
				else:B=str(A.venv_path/_c/_J)
			else:B=A.selected_python[_B][0]if isinstance(A.selected_python[_B],list)else A.selected_python[_B]
			C=subprocess.run([B,'-c',f'import {import_name}; print("OK")'],capture_output=_A,text=_A,timeout=10);return C.returncode==0 and'OK'in C.stdout
		except Exception:return _C
	def _show_core_error(A,missing_core):
		D='  2. ';C='  1. ';B=missing_core;print();print(ASCIIArt.DIVIDER_THICK);E=A.lang.get(_AL,_BX);print(Colors.FAIL+E+Colors.ENDC);print(ASCIIArt.DIVIDER_THICK);F=A.lang.get(_AK,'Missing core packages:');print(f"\n{Colors.FAIL}{F}{Colors.ENDC}")
		for G in B:print(f"  • {G}")
		H=A.lang.get(_AM,_BU);print(f"\n{Colors.OKBLUE}{H}{Colors.ENDC}");print(C+A.lang.get(_AN,'Installation interrupted'));print(D+A.lang.get(_AO,'Disk or network issues'));print('  3. '+A.lang.get(_AP,'Incompatible Python'));print('  4. '+A.lang.get(_AQ,_BV));I=A.lang.get(_AT,_BZ);print(f"\n{Colors.CYAN}{I}{Colors.ENDC}");print(C+A.lang.get(_AR,_BY));J=' '.join(B);print(f"     pip install --upgrade {J}");print();print(D+A.lang.get(_AS,'Consult troubleshooting:'));K='https://vnstocks.com/onboard-member/cai-dat-go-loi/giai-quyet-loi-thuong-gap';print(f"     {Colors.UNDERLINE}{K}{Colors.ENDC}");print();return _C
	def run_vnstock_installer(A,api_key=_D):
		Q='✅ Successful:';P='VNSTOCK_VENV_TYPE';K=api_key;J='❌ Failed:';I='ERROR';A.print_step(6,6,_v);R=Path(__file__).parent;G=R/'vnstock-installer.py'
		if not G.exists():A.print_error(f"Installer not found: {G}");return _C
		A.log('Running vnstock-installer.py',_F)
		if A.is_colab or A.is_codespaces:E=A.selected_python[_B][0]if isinstance(A.selected_python[_B],list)else A.selected_python[_B]
		elif A.venv_path and A.venv_type!=_E:
			if os.name==_P:E=str(A.venv_path/_b/_Z)
			else:E=str(A.venv_path/_c/_J)
		else:E=A.selected_python[_B][0]if isinstance(A.selected_python[_B],list)else A.selected_python[_B]
		C=os.environ.copy();C[_Bc]=A.language
		if A.is_colab:C[P]=_E;L=_AV;C['VNSTOCK_CONFIG_PATH']=L;Path(L).mkdir(parents=_A,exist_ok=_A)
		else:
			C[P]=A.venv_type or _AW
			if A.venv_path:C['VNSTOCK_VENV_PATH']=str(A.venv_path)
		if K:C[_Bb]=K
		try:
			D=subprocess.Popen([E,str(G)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=_A,env=C,bufsize=1);M,W=D.communicate(timeout=600);F=0;N=0;O=_C
			for B in M.split(_L):
				if'device limit exceeded'in B.lower():O=_A;break
			if O:
				if A.is_vietnamese:print(f"\n{Colors.FAIL}❌ Vượt quá giới hạn thiết bị!{Colors.ENDC}");print(f"{Colors.WARNING}Gói Golden của bạn chỉ cho phép 2 thiết bị mỗi hệ điều hành.{Colors.ENDC}");print(f"{Colors.CYAN}Hướng dẫn giải quyết:{Colors.ENDC}");print('  1. Vào trang: https://vnstocks.com/account?section=devices');print('  2. Xóa các thiết bị không còn sử dụng');print('  3. Chạy lại installer');print(f"\n{Colors.YELLOW}Sau khi xóa thiết bị, chạy lại lệnh cài đặt.{Colors.ENDC}")
				else:print(f"\n{Colors.FAIL}❌ Device limit exceeded!{Colors.ENDC}");print(f"{Colors.WARNING}Your Golden plan allows only 2 devices per OS.{Colors.ENDC}");print(f"{Colors.CYAN}How to fix:{Colors.ENDC}");print('  1. Go to: https://vnstocks.com/account?section=devices');print('  2. Remove unused devices');print('  3. Run installer again');print(f"\n{Colors.YELLOW}After removing devices, run the installer again.{Colors.ENDC}")
				A.log('Device limit exceeded - user needs to remove devices',I);return _C
			for B in M.split(_L):
				if B.strip():
					if'error'in B.lower()or'failed'in B.lower():
						print(f"{Colors.FAIL}{B}{Colors.ENDC}")
						if J in B or'failed:'in B.lower():
							try:
								if J in B:H=B.split(J)[1];S=int(H.strip().split()[0]);F=S
							except Exception:pass
					elif'success'in B.lower()or _w in B.lower():
						print(f"{Colors.OKGREEN}{B}{Colors.ENDC}")
						if Q in B:
							try:H=B.split(Q)[1];N=int(H.strip().split()[0])
							except Exception:pass
					else:print(B)
			if F>0:T=f"VNStock installation failed: {F} packages";A.print_error(T);U=f"Check logs: {A.log_file}";A.print_warning(U);A.log(f"VNStock installer failed: {F} packages",I);return _C
			elif D.returncode==0 or N>0:A.print_success(_BR);A.log('VNStock installer completed','SUCCESS');return _A
			else:A.print_error(f"Installer failed with code {D.returncode}");A.log(f"Installer failed: code {D.returncode}",I);return _C
		except subprocess.TimeoutExpired:D.kill();A.print_error('Installer timeout (10 minutes)');return _C
		except Exception as V:A.print_error(f"Failed to run installer: {V}");return _C
	def show_usage_instructions(A):
		O='2. Start using VNStock:';N='2. Bắt đầu sử dụng VNStock:';A.print_step(7,7,_BS);print(f"\n{Colors.OKGREEN}{ASCIIArt.SUCCESS}{Colors.ENDC}")
		if A.language==_K:C='📚 Hướng Dẫn Nhanh:';D='1. Kết nối Drive, thêm ô lệnh sau và chạy đầu tiên:';E=N;F='💡 Lưu Ý Quan Trọng:';G='   • Các thư viện đã được lưu trữ vào Google Drive';H='   • Thông tin người dùng được lưu trữ để sử dụng nhanh vào phiên tiếp theo';I='   • Phiên làm việc sau: Chỉ cần thêm sys.path để dùng lại thư viện đã cài mà không cần chạy lại installer';J='1. Kích hoạt môi trường ảo:';K=N;L='📖 Tài Liệu & Xử Lý Sự Cố:';M='File log:'
		else:C='📚 Quick Start Guide:';D='1. Add to first cell:';E=O;F='💡 Important Notes:';G='   • Packages backed up to Drive';H='   • API key stored in Drive (persistent)';I='   • After restart: Just add sys.path (no reinstall!)';J='1. Activate virtual environment:';K=O;L='📖 Documentation & Troubleshooting:';M='Log file:'
		print(f"\n{Colors.BOLD}{C}{Colors.ENDC}");print(ASCIIArt.DIVIDER_DOT)
		if A.is_colab:print(f"\n{Colors.BOLD}⚠️  Sử dụng môi trường đã cài ở phiên làm việc tiếp theo:{Colors.ENDC}");B=f"\n{Colors.CYAN}{D}{Colors.ENDC}";print(B);print('import sys');print('sys.path.insert(0, "/content/drive/MyDrive/.venv")');print('!cp -r /content/drive/MyDrive/.vnstock /root/.vnstock');P=f"\n{Colors.CYAN}{E}{Colors.ENDC}";print(P);print('from vnstock_data import Listing');print('Listing().all_symbols()');print(f"\n{Colors.BOLD}{F}{Colors.ENDC}");print(G);print(H);print(I)
		else:
			if A.venv_path:
				B=f"\n{Colors.CYAN}{J}{Colors.ENDC}";print(B)
				if os.name==_P:print(rf"{A.venv_path}\Scripts\activate")
				else:print(f"source {A.venv_path}/bin/activate")
			B=f"\n{Colors.CYAN}{K}{Colors.ENDC}";print(B);print(_J);print('>>> from vnstock_data import Listing');print('>>> Listing().all_symbols()')
		print(f"\n{Colors.CYAN}{L}{Colors.ENDC}");print('• Tài liệu chính: https://vnstocks.com/onboard-member');Q='https://vnstocks.com/onboard-member/cai-dat-go-loi/cai-dat-nang-cao';print(f"• Cài đặt nâng cao: {Q}");print(f"\n{Colors.GREY}{M} {A.log_file}{Colors.ENDC}");print(ASCIIArt.DIVIDER_THICK);print()
	def run(A,api_key_arg=_D):
		if A.is_colab:
			A.print_info(f"🔍 {A.lang[_A9]}")
			if not A.mount_google_drive():A.print_error(A.lang[_A8]);return _C
		if not A.detect_python_versions():return _C
		if not A.select_python_version():return _C
		if not A.select_venv_configuration():return _C
		if not A.is_colab:
			if not A.create_virtual_environment():return _C
		if A.is_colab:A.packages_before_sponsor=A._get_installed_packages();A.log(f"Snapshot: {len(A.packages_before_sponsor)} packages",_F)
		if not A.install_dependencies():return _C
		if not A.install_critical_dependencies():return _C
		E=A.get_api_key(provided_api_key=api_key_arg)
		if not A.run_vnstock_installer(api_key=E):return _C
		if A.is_colab:
			F=A._get_installed_packages();A.newly_installed_packages=F-A.packages_before_sponsor;A.log(f"Total new packages: {len(A.newly_installed_packages)}",_F)
			if not A.copy_vnstock_packages_to_drive():A.print_warning('Package backup to Drive failed (non-critical)')
		if A.is_colab:
			D=Path.home()/_e;B=Path(_AV)
			if D.exists():
				try:
					B.mkdir(parents=_A,exist_ok=_A)
					for C in D.iterdir():
						if C.is_file():shutil.copy2(C,B/C.name)
					A.log(f"Config backed up to Drive: {B}",_F)
				except Exception as G:A.log(f"Could not backup config to Drive: {G}",'WARNING')
		if not A.validate_installation():return _C
		A.show_usage_instructions();return _A
def main():
	E='store_true';D=sys.stdin.isatty();B=argparse.ArgumentParser(description='VNStock CLI Installer - Professional text-based installation',formatter_class=argparse.RawDescriptionHelpFormatter,epilog='\nExamples:\n  # Interactive mode (default)\n  python vnstock_cli.py\n  \n  # Non-interactive mode (for automation)\n  python vnstock_cli.py --non-interactive\n  \n  # Verbose output\n  python vnstock_cli.py --verbose\n  \nPerfect for:\n  - Google Colab notebooks\n  - Linux VPS servers\n  - Docker containers\n  - SSH sessions\n  - Headless environments\n        ');B.add_argument('--non-interactive',action=E,help='Run without prompts (for automation)');B.add_argument('--verbose',action=E,help='Show detailed output');B.add_argument('--language','--lang',choices=[_K,'en'],default=_K,help='Interface language: vi (Vietnamese) or en (English). Default: vi');B.add_argument('--api-key',type=str,default=_D,help='VNStock API key for sponsor package installation');A=B.parse_args()
	if not D:A.non_interactive=_A
	print(_L+Colors.VNSTOCK_GREEN+ASCIIArt.LOGO+Colors.ENDC);F=_BQ;print(Colors.VNSTOCK_GREEN+F+Colors.ENDC);print(Colors.VNSTOCK_GREEN+ASCIIArt.DIVIDER_THICK+Colors.ENDC);C=A.language
	if not A.non_interactive and D:
		print(f"\n{Colors.BOLD}Chọn ngôn ngữ / Select Language:{Colors.ENDC}");print('  1. Tiếng Việt (Vietnamese)');print('  2. English')
		try:
			G=input(f"\n{Colors.CYAN}Lựa chọn (Enter = 1): {Colors.ENDC}").strip()
			if G=='2':C='en'
		except EOFError:pass
	os.environ[_Bc]=C;H=VNStockCLIInstaller(interactive=not A.non_interactive,verbose=A.verbose,language=C)
	try:I=H.run(api_key_arg=A.api_key);sys.exit(0 if I else 1)
	except KeyboardInterrupt:print(f"\n\n{Colors.WARNING}Installation cancelled by user.{Colors.ENDC}");sys.exit(1)
	except Exception as J:print(f"\n\n{Colors.FAIL}Unexpected error: {J}{Colors.ENDC}");sys.exit(1)
if __name__=='__main__':main()