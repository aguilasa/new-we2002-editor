#include "stdafx.h"
#include "ed.h"
#include "editOptForm.h"
#include "edDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

editOptForm::editOptForm(CWnd* pParent /*=NULL*/)
	: CDialog(editOptForm::IDD, pParent)
{
	//{{AFX_DATA_INIT(carattDlg)
	//}}AFX_DATA_INIT
}

void editOptForm::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(carattDlg)
	DDX_Control(pDX, CHK_EDITNAME, chk_edit_names);
	DDX_Control(pDX, CHK_EDITLOOK, chk_edit_age_height_weight_foot);
	DDX_Control(pDX, CHK_EDITCHAR, chk_edit_characteristics);
	DDX_Control(pDX, CHK_EDITNUMS, chk_edit_shirt_numbers);
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(editOptForm, CDialog)
	//{{AFX_MSG_MAP(carattDlg)
	ON_BN_CLICKED(CHK_EDITNAME, OnChkEditName)
	ON_BN_CLICKED(CHK_EDITLOOK, OnChkEditLook)
	ON_BN_CLICKED(CHK_EDITCHAR, OnChkEditChar)
	ON_BN_CLICKED(CHK_EDITNUMS, OnChkEditNums)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// carattDlg message handlers

BOOL editOptForm::OnInitDialog() 
{

	CDialog::OnInitDialog();

	chk_edit_names.SetCheck(edit_names);
	chk_edit_age_height_weight_foot.SetCheck(edit_age_height_weight_foot);
	chk_edit_characteristics.SetCheck(edit_characteristics);
	chk_edit_shirt_numbers.SetCheck(edit_shirt_numbers);
	return TRUE;
}

void editOptForm::OnChkEditName() 
{
	edit_names = chk_edit_names.GetCheck();
}

void editOptForm::OnChkEditLook() 
{
	edit_age_height_weight_foot = chk_edit_age_height_weight_foot.GetCheck();
}

void editOptForm::OnChkEditChar() 
{
	edit_characteristics = chk_edit_characteristics.GetCheck();
}

void editOptForm::OnChkEditNums() 
{
	edit_shirt_numbers = chk_edit_shirt_numbers.GetCheck();
}
