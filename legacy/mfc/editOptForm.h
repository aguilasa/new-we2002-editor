#if !defined(AFX_EDITOPTFORM_H__9DFA2EC9_9713_11D6_9298_ED1FD355C71E__INCLUDED_)
#define AFX_EDITOPTFORM_H__9DFA2EC9_9713_11D6_9298_ED1FD355C71E__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif

class editOptForm : public CDialog
{
public:
	int edit_names;
	int edit_age_height_weight_foot;
	int edit_characteristics;
	int edit_shirt_numbers;
	editOptForm(CWnd* pParent = NULL);   // standard constructor
		
	enum { IDD = DLG_EDITOPT };
	CButton	chk_edit_names;
	CButton	chk_edit_age_height_weight_foot;
	CButton	chk_edit_characteristics;
	CButton chk_edit_shirt_numbers;

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support

protected:
	virtual BOOL OnInitDialog();
	afx_msg void OnChkEditName();
	afx_msg void OnChkEditLook();
	afx_msg void OnChkEditChar();
	afx_msg void OnChkEditNums();

	DECLARE_MESSAGE_MAP()
};

#endif