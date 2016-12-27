[System.Runtime.InteropServices.Guid("86580e95-2b14-8de9-4fa3-937898e28165"),
 Rhino.Commands.CommandStyle(Rhino.Commands.Style.ScriptRunner)]
public class Command_Numberer : Rhino.Commands.Command
{
  public override string EnglishName
  {
    get { return "Numberer"; }
  }

  private Rhino.Runtime.PythonScript m_script;
  private Rhino.Runtime.PythonCompiledCode m_compiledCode;
  protected override Rhino.Commands.Result RunCommand(Rhino.RhinoDoc doc, Rhino.Commands.RunMode mode)
  {
    CompilerPlugin.LoadLibraries();

    if (m_compiledCode == null)
    {
      System.Resources.ResourceManager rm = new System.Resources.ResourceManager("ScriptCode",
                                                System.Reflection.Assembly.GetExecutingAssembly());
      string source = rm.GetString("Numberer");
      source = DecryptString(source);
      m_script = Rhino.Runtime.PythonScript.Create();
      m_compiledCode = m_script.Compile(source);
    }

    if (m_compiledCode == null)
    {
      Rhino.RhinoApp.WriteLine("The script code for {0} could not be retrieved or compiled.", EnglishName);
      return Rhino.Commands.Result.Failure;
    }
    
    m_script.ScriptContextDoc = doc;
    m_script.SetVariable("__name__", "__main__");

    m_compiledCode.Execute(m_script);
    return Rhino.Commands.Result.Success;
  }

  private string DecryptString(string text)
  {
    if (text == null) { throw new System.ArgumentNullException("text"); }
    if (text.Length == 0) { return string.Empty; }

    byte[] data = System.Convert.FromBase64String(text);

    System.Security.Cryptography.RijndaelManaged rijndael = new System.Security.Cryptography.RijndaelManaged();
    rijndael.KeySize = 128;
    rijndael.BlockSize = 128;

    System.Guid key = new System.Guid("86580e95-2b14-8de9-4fa3-937898e28165");
    rijndael.Key = key.ToByteArray();
    rijndael.IV = key.ToByteArray();
    rijndael.Mode = System.Security.Cryptography.CipherMode.CBC;
    rijndael.Padding = System.Security.Cryptography.PaddingMode.PKCS7;

    System.Security.Cryptography.ICryptoTransform decryptor = rijndael.CreateDecryptor();
    byte[] result = decryptor.TransformFinalBlock(data, 0, data.Length);

    return System.Text.Encoding.UTF8.GetString(result);
  }
}