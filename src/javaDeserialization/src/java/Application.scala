import com.alibaba.fastjson.JSON

import java.io.*
import scala.io.{Source, StdIn}
import scala.util.{Failure, Success, Using}

object Application:
  def main(args: Array[String]): Unit =
    def hexStringToByteArray(hexString: String): Array[Byte] =
      for i <- Range(0, hexString.length / 2).toArray yield
        ((Character.digit(hexString.charAt(i * 2), 16) << 4) + Character.digit(hexString.charAt(i * 2 + 1), 16)).toByte
    while true do
      val serialization = hexStringToByteArray(StdIn.readLine())
      val data = Using(ObjectInputStream(ByteArrayInputStream(serialization))) { oi => oi.readObject() }
      data.map(JSON.toJSONString) match
        case Success(data) => println(data)
        case Failure(e) => e.printStackTrace()
end Application
