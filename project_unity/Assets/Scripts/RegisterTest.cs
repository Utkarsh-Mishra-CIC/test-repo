using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using UnityEngine.SceneManagement;

using System.IO;
using System.IO.IsolatedStorage;
using System.Net;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;

public class RegisterTest : MonoBehaviour {

    public InputField Username;
    public InputField Password;
    public InputField Confirm;
    public InputField Email;
    public Dropdown Gender;
    public Text UserType;
    string url = "https://localhost:5000/register";

    public void Register()
    {
        ServicePointManager.ServerCertificateValidationCallback = TrustCertificate;
        StartCoroutine(postRequest());
    }

    IEnumerator postRequest()
    {
        string cookie = null;
        {
            WWWForm form = new WWWForm();
            form.AddField("username", Username.text);
            form.AddField("password", Password.text);
            form.AddField("confirm", Confirm.text);
            form.AddField("email", Email.text);
            form.AddField("usertype", UserType.text);
            if (Gender.options[Gender.value].text == "Select") {
                form.AddField("gender", "");
            }
            else
            {
                form.AddField("gender", Gender.options[Gender.value].text);
            }
            Debug.Log("Sending Login request");
            using (UnityWebRequest www = UnityWebRequest.Post(url, form))
            {
                yield return www.SendWebRequest();
                if (!(www.isNetworkError || www.isHttpError))
                {
                    if (www.GetResponseHeaders().ContainsKey("Set-Cookie"))
                        cookie = www.GetResponseHeaders()["Set-Cookie"];
                    if (www.downloadHandler.text.Contains("Trainee"))
                    {
                        SceneManager.LoadScene("Demo2");
                    }
                    else if (www.downloadHandler.text.Contains("Expert"))
                    {
                        //GUIManager.GetComponent<UIManager>().SwitchToScreen(signIn_ExpertScreen);
                    }
                    else
                    {
                        // signIn_FailureScreen.SetActive(true);
                    }
                }
            }
        }
    }

    private static bool TrustCertificate(object sender, X509Certificate x509Certificate, X509Chain x509Chain, SslPolicyErrors sslPolicyErrors)
    {
        // all Certificates are accepted
        return true;
    }
}
