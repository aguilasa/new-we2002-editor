#include "stdafx.h"
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <vector>

#include <curl/curl.h>

using namespace std;

string remove_spaces(const string &s)
{
  int first = 0;
  int last = s.size() - 1;
  while (first >= 0 && (s[first] == ' ' || s[first] == '\t'))
    ++first;
  while (last >= 0 && (s[last] == ' ' || s[last] == '\t'))
    --last;
  return s.substr(first, last - first + 1);
}

vector<string> &splitOutsideDelimitingChars(const string &s, char openDelim, char closeDelim, vector<string> &elems) {
    stringstream ss(s);
    string item;
    while (getline(ss, item, openDelim)) {
        elems.push_back(item);
		getline(ss, item, closeDelim);
    }
    return elems;
}
vector<string> splitOutsideDelimitingChars(const string &s, char openDelim, char closeDelim) {
    vector<string> elems;
    splitOutsideDelimitingChars(s, openDelim, closeDelim, elems);
    return elems;
}

vector<string> &split(const string &s, char delim, vector<string> &elems) {
    stringstream ss(s);
    string item;
    while (getline(ss, item, delim)) {
        elems.push_back(item);
    }
    return elems;
}
vector<string> split(const string &s, char delim) {
    vector<string> elems;
    split(s, delim, elems);
    return elems;
}

// callback function writes data to a std::ostream
static size_t data_write(void* buf, size_t size, size_t nmemb, void* userp)
{
	if(userp)
	{
		std::ostream& os = *static_cast<std::ostream*>(userp);
		std::streamsize len = size * nmemb;
		if(os.write(static_cast<char*>(buf), len))
			return len;
	}

	return 0;
}

/**
 * timeout is in seconds
 **/
CURLcode curl_read(const std::string& url, std::ostream& os, long timeout = 30)
{
	CURLcode code(CURLE_FAILED_INIT);
	CURL* curl = curl_easy_init();

	if(curl)
	{
		if(CURLE_OK == (code = curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, &data_write))
		&& CURLE_OK == (code = curl_easy_setopt(curl, CURLOPT_NOPROGRESS, 1L))
		&& CURLE_OK == (code = curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L))
		//&& CURLE_OK == (code = curl_easy_setopt(curl, CURLOPT_USERAGENT, "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.0.3705;)"))
		&& CURLE_OK == (code = curl_easy_setopt(curl, CURLOPT_FILE, &os))
		&& CURLE_OK == (code = curl_easy_setopt(curl, CURLOPT_TIMEOUT, timeout))
		&& CURLE_OK == (code = curl_easy_setopt(curl, CURLOPT_URL, url.c_str())))
		{
			code = curl_easy_perform(curl);
		}
		curl_easy_cleanup(curl);
	}
	return code;
}

string getURLcontent(const string &link){
	curl_global_init(CURL_GLOBAL_ALL);
	ostringstream oss;
	string html = "";
	if(CURLE_OK == curl_read(link, oss))
	{
		// Web page successfully written to string
		html = oss.str();
	}
	return html;
}