// graf.cpp : implementation file
//

#include "stdafx.h"
#include "ed.h"
#include "graf.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// graf dialog


graf::graf(CWnd* pParent /*=NULL*/)
	: CDialog(graf::IDD, pParent)
{
	//{{AFX_DATA_INIT(graf)
	//}}AFX_DATA_INIT
}


void graf::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(graf)
	DDX_Control(pDX, TXT_2MAG_COL9, txt_2mag9);
	DDX_Control(pDX, TXT_2MAG_COL8, txt_2mag8);
	DDX_Control(pDX, TXT_2MAG_COL7, txt_2mag7);
	DDX_Control(pDX, TXT_2MAG_COL6, txt_2mag6);
	DDX_Control(pDX, TXT_2MAG_COL5, txt_2mag5);
	DDX_Control(pDX, TXT_2MAG_COL4, txt_2mag4);
	DDX_Control(pDX, TXT_2MAG_COL3, txt_2mag3);
	DDX_Control(pDX, TXT_2MAG_COL2, txt_2mag2);
	DDX_Control(pDX, TXT_2MAG_COL14, txt_2mag14);
	DDX_Control(pDX, TXT_2MAG_COL13, txt_2mag13);
	DDX_Control(pDX, TXT_2MAG_COL12, txt_2mag12);
	DDX_Control(pDX, TXT_2MAG_COL11, txt_2mag11);
	DDX_Control(pDX, TXT_2MAG_COL10, txt_2mag10);
	DDX_Control(pDX, TXT_2MAG_COL1, txt_2mag1);
	DDX_Control(pDX, TXT_1MAG_COL9, txt_1mag9);
	DDX_Control(pDX, TXT_1MAG_COL8, txt_1mag8);
	DDX_Control(pDX, TXT_1MAG_COL7, txt_1mag7);
	DDX_Control(pDX, TXT_1MAG_COL6, txt_1mag6);
	DDX_Control(pDX, TXT_1MAG_COL5, txt_1mag5);
	DDX_Control(pDX, TXT_1MAG_COL4, txt_1mag4);
	DDX_Control(pDX, TXT_1MAG_COL3, txt_1mag3);
	DDX_Control(pDX, TXT_1MAG_COL2, txt_1mag2);
	DDX_Control(pDX, TXT_1MAG_COL14, txt_1mag14);
	DDX_Control(pDX, TXT_1MAG_COL13, txt_1mag13);
	DDX_Control(pDX, TXT_1MAG_COL12, txt_1mag12);
	DDX_Control(pDX, TXT_1MAG_COL11, txt_1mag11);
	DDX_Control(pDX, TXT_1MAG_COL1, txt_1mag1);
	DDX_Control(pDX, TXT_1MAG_COL10, txt_1mag10);
	DDX_Control(pDX, TXT_BAND_STILE, txt_band_stile);
	DDX_Control(pDX, TXT_BAND_COL9, txt_band_col9);
	DDX_Control(pDX, TXT_BAND_COL8, txt_band_col8);
	DDX_Control(pDX, TXT_BAND_COL7, txt_band_col7);
	DDX_Control(pDX, TXT_BAND_COL6, txt_band_col6);
	DDX_Control(pDX, TXT_BAND_COL5, txt_band_col5);
	DDX_Control(pDX, TXT_BAND_COL4, txt_band_col4);
	DDX_Control(pDX, TXT_BAND_COL3, txt_band_col3);
	DDX_Control(pDX, TXT_BAND_COL2, txt_band_col2);
	DDX_Control(pDX, TXT_BAND_COL15, txt_band_col15);
	DDX_Control(pDX, TXT_BAND_COL14, txt_band_col14);
	DDX_Control(pDX, TXT_BAND_COL13, txt_band_col13);
	DDX_Control(pDX, TXT_BAND_COL12, txt_band_col12);
	DDX_Control(pDX, TXT_BAND_COL11, txt_band_col11);
	DDX_Control(pDX, TXT_BAND_COL10, txt_band_col10);
	DDX_Control(pDX, TXT_BAND_COL1, txt_band_col1);
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(graf, CDialog)
	//{{AFX_MSG_MAP(graf)
    ON_EN_KILLFOCUS(TXT_BAND_STILE, OnKillfocusBandStile)
	ON_EN_KILLFOCUS(TXT_BAND_COL1, OnKillfocusBandCol1)
	ON_EN_KILLFOCUS(TXT_BAND_COL2, OnKillfocusBandCol2)
	ON_EN_KILLFOCUS(TXT_BAND_COL3, OnKillfocusBandCol3)
	ON_EN_KILLFOCUS(TXT_BAND_COL4, OnKillfocusBandCol4)
	ON_EN_KILLFOCUS(TXT_BAND_COL5, OnKillfocusBandCol5)
	ON_EN_KILLFOCUS(TXT_BAND_COL6, OnKillfocusBandCol6)
	ON_EN_KILLFOCUS(TXT_BAND_COL7, OnKillfocusBandCol7)
	ON_EN_KILLFOCUS(TXT_BAND_COL8, OnKillfocusBandCol8)
	ON_EN_KILLFOCUS(TXT_BAND_COL9, OnKillfocusBandCol9)
	ON_EN_KILLFOCUS(TXT_BAND_COL10, OnKillfocusBandCol10)
	ON_EN_KILLFOCUS(TXT_BAND_COL11, OnKillfocusBandCol11)
	ON_EN_KILLFOCUS(TXT_BAND_COL12, OnKillfocusBandCol12)
	ON_EN_KILLFOCUS(TXT_BAND_COL13, OnKillfocusBandCol13)
	ON_EN_KILLFOCUS(TXT_BAND_COL14, OnKillfocusBandCol14)
	ON_EN_KILLFOCUS(TXT_BAND_COL15, OnKillfocusBandCol15)
	ON_BN_CLICKED(IDC_BUTTONINB, OnImportaBandiera)
	ON_BN_CLICKED(IDC_BUTTONESB, OnEsportaBandiera)
	ON_EN_KILLFOCUS(TXT_1MAG_COL1, OnKillfocus1magCol1)
	ON_EN_KILLFOCUS(TXT_1MAG_COL2, OnKillfocus1magCol2)
	ON_EN_KILLFOCUS(TXT_1MAG_COL3, OnKillfocus1magCol3)
	ON_EN_KILLFOCUS(TXT_1MAG_COL4, OnKillfocus1magCol4)
	ON_EN_KILLFOCUS(TXT_1MAG_COL5, OnKillfocus1magCol5)
	ON_EN_KILLFOCUS(TXT_1MAG_COL6, OnKillfocus1magCol6)
	ON_EN_KILLFOCUS(TXT_1MAG_COL7, OnKillfocus1magCol7)
	ON_EN_KILLFOCUS(TXT_1MAG_COL8, OnKillfocus1magCol8)
	ON_EN_KILLFOCUS(TXT_1MAG_COL9, OnKillfocus1magCol9)
	ON_EN_KILLFOCUS(TXT_1MAG_COL10, OnKillfocus1magCol10)
	ON_EN_KILLFOCUS(TXT_1MAG_COL11, OnKillfocus1magCol11)
	ON_EN_KILLFOCUS(TXT_1MAG_COL12, OnKillfocus1magCol12)
	ON_EN_KILLFOCUS(TXT_1MAG_COL13, OnKillfocus1magCol13)
	ON_EN_KILLFOCUS(TXT_1MAG_COL14, OnKillfocus1magCol14)
	ON_EN_KILLFOCUS(TXT_2MAG_COL1, OnKillfocus2magCol1)
	ON_EN_KILLFOCUS(TXT_2MAG_COL2, OnKillfocus2magCol2)
	ON_EN_KILLFOCUS(TXT_2MAG_COL3, OnKillfocus2magCol3)
	ON_EN_KILLFOCUS(TXT_2MAG_COL4, OnKillfocus2magCol4)
	ON_EN_KILLFOCUS(TXT_2MAG_COL5, OnKillfocus2magCol5)
	ON_EN_KILLFOCUS(TXT_2MAG_COL6, OnKillfocus2magCol6)
	ON_EN_KILLFOCUS(TXT_2MAG_COL7, OnKillfocus2magCol7)
	ON_EN_KILLFOCUS(TXT_2MAG_COL8, OnKillfocus2magCol8)
	ON_EN_KILLFOCUS(TXT_2MAG_COL9, OnKillfocus2magCol9)
	ON_EN_KILLFOCUS(TXT_2MAG_COL10, OnKillfocus2magCol10)
	ON_EN_KILLFOCUS(TXT_2MAG_COL11, OnKillfocus2magCol11)
	ON_EN_KILLFOCUS(TXT_2MAG_COL12, OnKillfocus2magCol12)
	ON_EN_KILLFOCUS(TXT_2MAG_COL13, OnKillfocus2magCol13)
	ON_EN_KILLFOCUS(TXT_2MAG_COL14, OnKillfocus2magCol14)
	ON_BN_CLICKED(IDC_BUTTON1IM, OnImportaMaglia1)
	ON_BN_CLICKED(IDC_BUTTON1EM, OnEsportaMaglia1)
	ON_BN_CLICKED(IDC_BUTTON2IM, OnImportaMaglia2)
	ON_BN_CLICKED(IDC_BUTTON2EM, OnEsportaMaglia2)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// graf message handlers


void graf::OnKillfocusBandStile() 
{
	CString aux;
	txt_band_stile.GetWindowText(aux);
	stile_bandiera = atoi(aux);
}

void graf::OnKillfocusBandCol1() 
{
	focusBand(&txt_band_col1,0);
}

void graf::OnKillfocusBandCol2() 
{
	focusBand(&txt_band_col2,1);
}

void graf::OnKillfocusBandCol3() 
{
	focusBand(&txt_band_col3,2);
}

void graf::OnKillfocusBandCol4() 
{
	focusBand(&txt_band_col4,3);
}

void graf::OnKillfocusBandCol5() 
{
	focusBand(&txt_band_col5,4);
}

void graf::OnKillfocusBandCol6() 
{
	focusBand(&txt_band_col6,5);
}

void graf::OnKillfocusBandCol7() 
{
	focusBand(&txt_band_col7,6);
}

void graf::OnKillfocusBandCol8() 
{
	focusBand(&txt_band_col8,7);
}

void graf::OnKillfocusBandCol9() 
{
	focusBand(&txt_band_col9,8);
}

void graf::OnKillfocusBandCol15() 
{
	focusBand(&txt_band_col15,14);
}

void graf::OnKillfocusBandCol14() 
{
	focusBand(&txt_band_col14,13);
}

void graf::OnKillfocusBandCol13() 
{
	focusBand(&txt_band_col13,12);
}

void graf::OnKillfocusBandCol12() 
{
	focusBand(&txt_band_col12,11);
}

void graf::OnKillfocusBandCol11() 
{
	focusBand(&txt_band_col11,10);
}

void graf::OnKillfocusBandCol10() 
{
	focusBand(&txt_band_col10,9);
}

BOOL graf::OnInitDialog() 
{
	CDialog::OnInitDialog();
//	char strint[20];
	// bandiere
	txt_band_stile.LimitText(2);
	txt_band_col1.LimitText(5);
	txt_band_col2.LimitText(5);
	txt_band_col3.LimitText(5);
	txt_band_col4.LimitText(5);
	txt_band_col5.LimitText(5);
	txt_band_col6.LimitText(5);
	txt_band_col7.LimitText(5);
	txt_band_col8.LimitText(5);
	txt_band_col9.LimitText(5);
	txt_band_col10.LimitText(5);
	txt_band_col11.LimitText(5);
	txt_band_col12.LimitText(5);
	txt_band_col13.LimitText(5);
	txt_band_col14.LimitText(5);
	txt_band_col15.LimitText(5);//16^4=65535 

	txt_1mag1.LimitText(5);
	txt_1mag2.LimitText(5);
	txt_1mag3.LimitText(5);
	txt_1mag4.LimitText(5);
	txt_1mag5.LimitText(5);
	txt_1mag6.LimitText(5);
	txt_1mag7.LimitText(5);
	txt_1mag8.LimitText(5);
	txt_1mag9.LimitText(5);
	txt_1mag10.LimitText(5);
	txt_1mag11.LimitText(5);
	txt_1mag12.LimitText(5);
	txt_1mag13.LimitText(5);
	txt_1mag14.LimitText(5);

	txt_2mag1.LimitText(5);
	txt_2mag2.LimitText(5);
	txt_2mag3.LimitText(5);
	txt_2mag4.LimitText(5);
	txt_2mag5.LimitText(5);
	txt_2mag6.LimitText(5);
	txt_2mag7.LimitText(5);
	txt_2mag8.LimitText(5);
	txt_2mag9.LimitText(5);
	txt_2mag10.LimitText(5);
	txt_2mag11.LimitText(5);
	txt_2mag12.LimitText(5);
	txt_2mag13.LimitText(5);
	txt_2mag14.LimitText(5);

	if((id>56 && id<64) || (id == 69 || id == 86))
	//disabilita colori bandiera classic
	//newcastle+parma
	{
		txt_band_col1.EnableWindow(FALSE);
		txt_band_col2.EnableWindow(FALSE);
		txt_band_col3.EnableWindow(FALSE);
		txt_band_col4.EnableWindow(FALSE);
		txt_band_col5.EnableWindow(FALSE);
		txt_band_col6.EnableWindow(FALSE);
		txt_band_col7.EnableWindow(FALSE);
		txt_band_col8.EnableWindow(FALSE);
		txt_band_col9.EnableWindow(FALSE);
		txt_band_col10.EnableWindow(FALSE);
		txt_band_col11.EnableWindow(FALSE);
		txt_band_col12.EnableWindow(FALSE);
		txt_band_col13.EnableWindow(FALSE);
		txt_band_col14.EnableWindow(FALSE);
		txt_band_col15.EnableWindow(FALSE);
	} else
	{
		txt_band_stile.EnableWindow(TRUE);
		txt_band_col1.EnableWindow(TRUE);
		txt_band_col2.EnableWindow(TRUE);
		txt_band_col3.EnableWindow(TRUE);
		txt_band_col4.EnableWindow(TRUE);
		txt_band_col5.EnableWindow(TRUE);
		txt_band_col6.EnableWindow(TRUE);
		txt_band_col7.EnableWindow(TRUE);
		txt_band_col8.EnableWindow(TRUE);
		txt_band_col9.EnableWindow(TRUE);
		txt_band_col10.EnableWindow(TRUE);
		txt_band_col11.EnableWindow(TRUE);
		txt_band_col12.EnableWindow(TRUE);
		txt_band_col13.EnableWindow(TRUE);
		txt_band_col14.EnableWindow(TRUE);
		txt_band_col15.EnableWindow(TRUE);
	}

	graf::carica();
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

void graf::carica()
{
	char strint[20];
	_itoa(int(stile_bandiera), strint, 10);
	txt_band_stile.SetWindowText(strint);
	_ultoa(long(col_bandiera[0]), strint, 10);
	txt_band_col1.SetWindowText(strint);
	_ultoa(long(col_bandiera[1]), strint, 10);
	txt_band_col2.SetWindowText(strint);
	_ultoa(long(col_bandiera[2]), strint, 10);
	txt_band_col3.SetWindowText(strint);
	_ultoa(long(col_bandiera[3]), strint, 10);
	txt_band_col4.SetWindowText(strint);
	_ultoa(long(col_bandiera[4]), strint, 10);
	txt_band_col5.SetWindowText(strint);
	_ultoa(long(col_bandiera[5]), strint, 10);
	txt_band_col6.SetWindowText(strint);
	_ultoa(long(col_bandiera[6]), strint, 10);
	txt_band_col7.SetWindowText(strint);
	_ultoa(long(col_bandiera[7]), strint, 10);
	txt_band_col8.SetWindowText(strint);
	_ultoa(long(col_bandiera[8]), strint, 10);
	txt_band_col9.SetWindowText(strint);
	_ultoa(long(col_bandiera[9]), strint, 10);
	txt_band_col10.SetWindowText(strint);
	_ultoa(long(col_bandiera[10]), strint, 10);
	txt_band_col11.SetWindowText(strint);
	_ultoa(long(col_bandiera[11]), strint, 10);
	txt_band_col12.SetWindowText(strint);
	_ultoa(long(col_bandiera[12]), strint, 10);
	txt_band_col13.SetWindowText(strint);
	_ultoa(long(col_bandiera[13]), strint, 10);
	txt_band_col14.SetWindowText(strint);
	_ultoa(long(col_bandiera[14]), strint, 10);
	txt_band_col15.SetWindowText(strint);

	_ultoa(long(col_maglia1[2]), strint, 10);
	txt_1mag1.SetWindowText(strint);
	_ultoa(long(col_maglia1[3]), strint, 10);
	txt_1mag2.SetWindowText(strint);
	_ultoa(long(col_maglia1[4]), strint, 10);
	txt_1mag3.SetWindowText(strint);
	_ultoa(long(col_maglia1[5]), strint, 10);
	txt_1mag4.SetWindowText(strint);
	_ultoa(long(col_maglia1[6]), strint, 10);
	txt_1mag5.SetWindowText(strint);
	_ultoa(long(col_maglia1[7]), strint, 10);
	txt_1mag6.SetWindowText(strint);
	_ultoa(long(col_maglia1[8]), strint, 10);
	txt_1mag7.SetWindowText(strint);
	_ultoa(long(col_maglia1[9]), strint, 10);
	txt_1mag8.SetWindowText(strint);
	_ultoa(long(col_maglia1[10]), strint, 10);
	txt_1mag9.SetWindowText(strint);
	_ultoa(long(col_maglia1[11]), strint, 10);
	txt_1mag10.SetWindowText(strint);
	_ultoa(long(col_maglia1[12]), strint, 10);
	txt_1mag11.SetWindowText(strint);
	_ultoa(long(col_maglia1[13]), strint, 10);
	txt_1mag12.SetWindowText(strint);
	_ultoa(long(col_maglia1[14]), strint, 10);
	txt_1mag13.SetWindowText(strint);
	_ultoa(long(col_maglia1[15]), strint, 10);
	txt_1mag14.SetWindowText(strint);

	_ultoa(long(col_maglia2[2]), strint, 10);
	txt_2mag1.SetWindowText(strint);
	_ultoa(long(col_maglia2[3]), strint, 10);
	txt_2mag2.SetWindowText(strint);
	_ultoa(long(col_maglia2[4]), strint, 10);
	txt_2mag3.SetWindowText(strint);
	_ultoa(long(col_maglia2[5]), strint, 10);
	txt_2mag4.SetWindowText(strint);
	_ultoa(long(col_maglia2[6]), strint, 10);
	txt_2mag5.SetWindowText(strint);
	_ultoa(long(col_maglia2[7]), strint, 10);
	txt_2mag6.SetWindowText(strint);
	_ultoa(long(col_maglia2[8]), strint, 10);
	txt_2mag7.SetWindowText(strint);
	_ultoa(long(col_maglia2[9]), strint, 10);
	txt_2mag8.SetWindowText(strint);
	_ultoa(long(col_maglia2[10]), strint, 10);
	txt_2mag9.SetWindowText(strint);
	_ultoa(long(col_maglia2[11]), strint, 10);
	txt_2mag10.SetWindowText(strint);
	_ultoa(long(col_maglia2[12]), strint, 10);
	txt_2mag11.SetWindowText(strint);
	_ultoa(long(col_maglia2[13]), strint, 10);
	txt_2mag12.SetWindowText(strint);
	_ultoa(long(col_maglia2[14]), strint, 10);
	txt_2mag13.SetWindowText(strint);
	_ultoa(long(col_maglia2[15]), strint, 10);
	txt_2mag14.SetWindowText(strint);
}

void graf::OnKillfocus1magCol1() 
{
	focusMaglia(&txt_1mag1,2,1);
}

void graf::OnKillfocus1magCol2() 
{
	focusMaglia(&txt_1mag2,3,1);
}

void graf::OnKillfocus1magCol3() 
{
	focusMaglia(&txt_1mag3,4,1);
}

void graf::OnKillfocus1magCol4() 
{
	focusMaglia(&txt_1mag4,5,1);
}

void graf::OnKillfocus1magCol5() 
{
	focusMaglia(&txt_1mag5,6,1);
}

void graf::OnKillfocus1magCol6() 
{
	focusMaglia(&txt_1mag6,7,1);
}

void graf::OnKillfocus1magCol7() 
{
	focusMaglia(&txt_1mag7,8,1);
}

void graf::OnKillfocus1magCol8() 
{
	focusMaglia(&txt_1mag8,9,1);
}

void graf::OnKillfocus1magCol9() 
{
	focusMaglia(&txt_1mag9,10,1);
}

void graf::OnKillfocus1magCol10() 
{
	focusMaglia(&txt_1mag10,11,1);
}

void graf::OnKillfocus1magCol11() 
{
	focusMaglia(&txt_1mag11,12,1);
}

void graf::OnKillfocus1magCol12() 
{
	focusMaglia(&txt_1mag12,13,1);
}

void graf::OnKillfocus1magCol13() 
{
	focusMaglia(&txt_1mag13,14,1);
}

void graf::OnKillfocus1magCol14() 
{
	focusMaglia(&txt_1mag14,15,1);
}


void graf::OnKillfocus2magCol1() 
{
	focusMaglia(&txt_2mag1,2,2);
}

void graf::OnKillfocus2magCol2() 
{
	focusMaglia(&txt_2mag2,3,2);
}

void graf::OnKillfocus2magCol3() 
{
	focusMaglia(&txt_2mag3,4,2);
}

void graf::OnKillfocus2magCol4() 
{
	focusMaglia(&txt_2mag4,5,2);
}

void graf::OnKillfocus2magCol5() 
{
	focusMaglia(&txt_2mag5,6,2);
}

void graf::OnKillfocus2magCol6() 
{
	focusMaglia(&txt_2mag6,7,2);
}

void graf::OnKillfocus2magCol7() 
{
	focusMaglia(&txt_2mag7,8,2);
}

void graf::OnKillfocus2magCol8() 
{
	focusMaglia(&txt_2mag8,9,2);
}

void graf::OnKillfocus2magCol9() 
{
	focusMaglia(&txt_2mag9,10,2);
}

void graf::OnKillfocus2magCol10() 
{
	focusMaglia(&txt_2mag10,11,2);
}

void graf::OnKillfocus2magCol11() 
{
	focusMaglia(&txt_2mag11,12,2);
}

void graf::OnKillfocus2magCol12() 
{
	focusMaglia(&txt_2mag12,13,2);
}

void graf::OnKillfocus2magCol13() 
{
	focusMaglia(&txt_2mag13,14,2);
}

void graf::OnKillfocus2magCol14() 
{
	focusMaglia(&txt_2mag14,15,2);
}

void graf::focusBand(CEdit *txt,int k)
{
	CString aux;
	int i;
	txt->GetWindowText(aux);
	i = atoi(aux);
	if(i>65535)
		txt->SetWindowText("65535");
	txt->GetWindowText(aux);
	col_bandiera[k] = atoi(aux);
}

void graf::focusMaglia(CEdit *txt,int k,int m)
{
	CString aux;
	int i;
	txt->GetWindowText(aux);
	i = atoi(aux);
	if(i>65535)
		txt->SetWindowText("65535");
	txt->GetWindowText(aux);
	if(m == 1)
		col_maglia1[k] = atoi(aux);
	else if(m == 2)
		col_maglia2[k] = atoi(aux);
}

void graf::OnImportaMaglia1() 
{
	importaMaglia(1);
}

void graf::OnEsportaMaglia1() 
{
	esportaMaglia(1);
}

void graf::OnImportaMaglia2() 
{
	importaMaglia(2);
}

void graf::OnEsportaMaglia2() 
{
	esportaMaglia(2);
}

void graf::importaMaglia(int k)
{
	char path[_MAX_PATH];
	char drive[_MAX_DRIVE];
	char dir[_MAX_DIR];
	char filtro[] = "shirt file MANIA 2002 (*.m2002)|*.m2002|";
	char aux[10];
	CString nome_file,fil_path_programma;

	GetModuleFileName(AfxGetInstanceHandle(), path, MAX_PATH);
	_splitpath(path, drive, dir, NULL, NULL);
	fil_path_programma = drive;
	fil_path_programma += dir;

 	CFileDialog dlg(TRUE, NULL, NULL, OFN_HIDEREADONLY | OFN_OVERWRITEPROMPT, filtro, NULL );
	dlg.m_ofn.lpstrInitialDir = fil_path_programma;
	dlg.m_ofn.lpstrTitle = "SHIRT FILE TO IMPORT";
	if( IDOK == dlg.DoModal() )
		nome_file = dlg.m_ofn.lpstrFile;
	else
		return;
	CFile fil_ctrl(nome_file, CFile::modeRead | CFile::typeBinary );
	fil_ctrl.Seek(0,CFile::begin);
	fil_ctrl.Read(aux,8);
	aux[8] = NULL;
	if(strcmp(aux,"f.m.magl") != 0 || fil_ctrl.GetLength() != 40)
	{
		AfxMessageBox("Not right file!");
		return;
	}
	if(k == 1)
		fil_ctrl.Read(&col_maglia1,32);
	else if(k == 2)
		fil_ctrl.Read(&col_maglia2,32);
	fil_ctrl.Close();
	graf::carica();
	AfxMessageBox("Shirt imported !");
}

void graf::esportaMaglia(int k)
{
	char path[_MAX_PATH];
	char drive[_MAX_DRIVE];
	char dir[_MAX_DIR];
	char filtro[] = "shirt file MANIA 2002 (*.m2002)|*.m2002|";
	CString nome_file,fil_path_programma;

	GetModuleFileName(AfxGetInstanceHandle(), path, MAX_PATH);
	_splitpath(path, drive, dir, NULL, NULL);
	fil_path_programma = drive;
	fil_path_programma += dir;

	CFileDialog dlg(FALSE, NULL, NULL, OFN_HIDEREADONLY | OFN_EXPLORER | OFN_PATHMUSTEXIST | OFN_FILEMUSTEXIST, filtro, NULL );
	dlg.m_ofn.lpstrInitialDir = fil_path_programma;
	dlg.m_ofn.lpstrTitle = "SHIRT FILE TO EXPORT";
	if( IDOK == dlg.DoModal() )
		nome_file = dlg.m_ofn.lpstrFile;
	else
		return;
	if(nome_file.Right(6) != ".m2002")
		nome_file += ".m2002";
	CFile fil_ctrl(nome_file, CFile::modeReadWrite | CFile::typeBinary | CFile::modeCreate);
	fil_ctrl.Seek(0,CFile::begin);
	// salvataggio sul nuovo file
	fil_ctrl.Write("f.m.magl",8);
	if(k == 1)
		fil_ctrl.Write(&col_maglia1,32);
	else if(k == 2)
		fil_ctrl.Write(&col_maglia2,32);
	fil_ctrl.Close();
	AfxMessageBox("Shirt exported !");
}

void graf::OnImportaBandiera() 
{
	char path[_MAX_PATH];
	char drive[_MAX_DRIVE];
	char dir[_MAX_DIR];
	char filtro[] = "flag file MANIA 2002 (*.b2002)|*.b2002|";
	char aux[10];
	CString nome_file,fil_path_programma;

	//esclusione bandiere non indipendenti
	if(id>0 && id != 69 && id != 86 && (id<56 || id>63))
	{
		GetModuleFileName(AfxGetInstanceHandle(), path, MAX_PATH);
		_splitpath(path, drive, dir, NULL, NULL);
		fil_path_programma = drive;
		fil_path_programma += dir;

 		CFileDialog dlg(TRUE, NULL, NULL, OFN_HIDEREADONLY | OFN_OVERWRITEPROMPT, filtro, NULL );
		dlg.m_ofn.lpstrInitialDir = fil_path_programma;
		dlg.m_ofn.lpstrTitle = "FLAG FILE TO IMPORT";
		if( IDOK == dlg.DoModal() )
			nome_file = dlg.m_ofn.lpstrFile;
		else
			return;
		CFile fil_ctrl(nome_file, CFile::modeRead | CFile::typeBinary );
		fil_ctrl.Seek(0,CFile::begin);
		fil_ctrl.Read(aux,8);
		aux[8] = NULL;
		if(strcmp(aux,"f.m.band") != 0 || fil_ctrl.GetLength() != 41)
		{
			AfxMessageBox("Not right file !");
			return;
		}
		fil_ctrl.Read(&stile_bandiera,1);
		fil_ctrl.Read(&col_bandiera,32);
		fil_ctrl.Close();
		graf::carica();
		AfxMessageBox("Flag imported !");
	} else
		AfxMessageBox("Choose a team (that has \"indipendent\" flag too) !");
}

void graf::OnEsportaBandiera() 
{
	char path[_MAX_PATH];
	char drive[_MAX_DRIVE];
	char dir[_MAX_DIR];
	char filtro[] = "flag file MANIA 2002 (*.b2002)|*.b2002|";
	CString nome_file,fil_path_programma;

	//esclusione bandiere non indipendenti
	if(id>0 && id != 69 && id != 86 && (id<56 || id>63))
	{
		GetModuleFileName(AfxGetInstanceHandle(), path, MAX_PATH);
		_splitpath(path, drive, dir, NULL, NULL);
		fil_path_programma = drive;
		fil_path_programma += dir;

		CFileDialog dlg(FALSE, NULL, NULL, OFN_HIDEREADONLY | OFN_EXPLORER | OFN_PATHMUSTEXIST | OFN_FILEMUSTEXIST, filtro, NULL );
		dlg.m_ofn.lpstrInitialDir = fil_path_programma;
		dlg.m_ofn.lpstrTitle = "FLAG FILE TO EXPORT";
		do
		{
			if( IDOK == dlg.DoModal() )
				nome_file = dlg.m_ofn.lpstrFile;
			else
				return;
		} while(nome_file.Right(1) == "/" || nome_file.Right(7) == "/.b2002");
		if(nome_file.Right(6) != ".b2002")
			nome_file += ".b2002";
		CFile fil_ctrl(nome_file, CFile::modeReadWrite | CFile::typeBinary | CFile::modeCreate);
		fil_ctrl.Seek(0,CFile::begin);
		// salvataggio sul nuovo file
		fil_ctrl.Write("f.m.band",8);
		fil_ctrl.Write(&stile_bandiera,1);
		fil_ctrl.Write(&col_bandiera,32);
		fil_ctrl.Close();
		AfxMessageBox("Flag exported !");
	} else
		AfxMessageBox("Choose a team (that has \"indipendent\" flag too) !");
}
