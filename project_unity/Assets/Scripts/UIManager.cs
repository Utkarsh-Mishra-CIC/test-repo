using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;
public class UIManager : MonoBehaviour
{
    List<GameObject> screens = new List<GameObject>();
    public GameObject mainScreen;

    public void SwitchToScreen(GameObject es)
    {
        foreach (var s in screens)
            s.SetActive(false);

        es.SetActive(true);
    }

    public void SwitchToMainScreen()
    {
        SwitchToScreen(mainScreen);
    }

    void Start()
    {

        for (int i = 0; i < transform.childCount; ++i)
            screens.Add(transform.GetChild(i).gameObject);

    }
    public GameObject TraineeInfo;
    public void TraineeInfoPopUp()
    {
        TraineeInfo.SetActive(true);
    }
    public void SimulationTesst()
    {
        SceneManager.LoadScene("Demo2");
    }
    public void Exit()
    {
        Application.Quit();
    }
}
