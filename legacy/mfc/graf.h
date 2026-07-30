#if !defined(AFX_GRAF_H__1903DAC1_A381_11D6_9298_DA977BDACD1E__INCLUDED_)
#define AFX_GRAF_H__1903DAC1_A381_11D6_9298_DA977BDACD1E__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// graf.h : header file
//

/////////////////////////////////////////////////////////////////////////////
// graf dialog

class graf : public CDialog
{
// Construction
public:
	void esportaMaglia(int k);
	void importaMaglia(int k);
	void carica();
	char stile_bandiera;
	unsigned short col_bandiera[16];
	unsigned short col_maglia1[16];
	unsigned short col_maglia2[16];
	int id;

	void focusMaglia(CEdit *txt,int k,int m);
	void focusBand(CEdit *txt,int k);
	graf(CWnd* pParent = NULL);   // standard constructor
	

// Dialog Data
	//{{AFX_DATA(graf)
	enum { IDD = DLG_GRAF };
	CEdit	txt_2mag9;
	CEdit	txt_2mag8;
	CEdit	txt_2mag7;
	CEdit	txt_2mag6;
	CEdit	txt_2mag5;
	CEdit	txt_2mag4;
	CEdit	txt_2mag3;
	CEdit	txt_2mag2;
	CEdit	txt_2mag14;
	CEdit	txt_2mag13;
	CEdit	txt_2mag12;
	CEdit	txt_2mag11;
	CEdit	txt_2mag10;
	CEdit	txt_2mag1;
	CEdit	txt_1mag9;
	CEdit	txt_1mag8;
	CEdit	txt_1mag7;
	CEdit	txt_1mag6;
	CEdit	txt_1mag5;
	CEdit	txt_1mag4;
	CEdit	txt_1mag3;
	CEdit	txt_1mag2;
	CEdit	txt_1mag14;
	CEdit	txt_1mag13;
	CEdit	txt_1mag12;
	CEdit	txt_1mag11;
	CEdit	txt_1mag1;
	CEdit	txt_1mag10;
	CEdit	txt_band_stile;
	CEdit	txt_band_col9;
	CEdit	txt_band_col8;
	CEdit	txt_band_col7;
	CEdit	txt_band_col6;
	CEdit	txt_band_col5;
	CEdit	txt_band_col4;
	CEdit	txt_band_col3;
	CEdit	txt_band_col2;
	CEdit	txt_band_col15;
	CEdit	txt_band_col14;
	CEdit	txt_band_col13;
	CEdit	txt_band_col12;
	CEdit	txt_band_col11;
	CEdit	txt_band_col10;
	CEdit	txt_band_col1;
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(graf)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:

	// Generated message map functions
	//{{AFX_MSG(graf)
	afx_msg void OnKillfocusBandStile();
	afx_msg void OnKillfocusBandCol1();
	afx_msg void OnKillfocusBandCol2();
	afx_msg void OnKillfocusBandCol3();
	afx_msg void OnKillfocusBandCol4();
	afx_msg void OnKillfocusBandCol5();
	afx_msg void OnKillfocusBandCol6();
	afx_msg void OnKillfocusBandCol7();
	afx_msg void OnKillfocusBandCol8();
	afx_msg void OnKillfocusBandCol9();
	afx_msg void OnKillfocusBandCol10();
	afx_msg void OnKillfocusBandCol11();
	afx_msg void OnKillfocusBandCol12();
	afx_msg void OnKillfocusBandCol13();
	afx_msg void OnKillfocusBandCol14();
	afx_msg void OnKillfocusBandCol15();
	afx_msg void OnImportaBandiera();
	afx_msg void OnEsportaBandiera();
	virtual BOOL OnInitDialog();
	afx_msg void OnKillfocus1magCol1();
	afx_msg void OnKillfocus1magCol2();
	afx_msg void OnKillfocus1magCol3();
	afx_msg void OnKillfocus1magCol4();
	afx_msg void OnKillfocus1magCol5();
	afx_msg void OnKillfocus1magCol6();
	afx_msg void OnKillfocus1magCol7();
	afx_msg void OnKillfocus1magCol8();
	afx_msg void OnKillfocus1magCol9();
	afx_msg void OnKillfocus1magCol10();
	afx_msg void OnKillfocus1magCol11();
	afx_msg void OnKillfocus1magCol12();
	afx_msg void OnKillfocus1magCol13();
	afx_msg void OnKillfocus1magCol14();
	afx_msg void OnKillfocus2magCol1();
	afx_msg void OnKillfocus2magCol2();
	afx_msg void OnKillfocus2magCol3();
	afx_msg void OnKillfocus2magCol4();
	afx_msg void OnKillfocus2magCol5();
	afx_msg void OnKillfocus2magCol6();
	afx_msg void OnKillfocus2magCol7();
	afx_msg void OnKillfocus2magCol8();
	afx_msg void OnKillfocus2magCol9();
	afx_msg void OnKillfocus2magCol10();
	afx_msg void OnKillfocus2magCol11();
	afx_msg void OnKillfocus2magCol12();
	afx_msg void OnKillfocus2magCol13();
	afx_msg void OnKillfocus2magCol14();
	afx_msg void OnImportaMaglia1();
	afx_msg void OnEsportaMaglia1();
	afx_msg void OnImportaMaglia2();
	afx_msg void OnEsportaMaglia2();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_GRAF_H__1903DAC1_A381_11D6_9298_DA977BDACD1E__INCLUDED_)
